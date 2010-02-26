import sys
import logging
import os
from optparse import make_option
from django.core.management.base import CommandError
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from saucebrush.filters import FieldAdder, FieldMerger, FieldModifier, FieldRenamer,\
    Filter
from saucebrush.emitters import CSVEmitter, DebugEmitter
from saucebrush.sources import CSVSource

from dcdata.utils.dryrub import CountEmitter, FieldCountValidator
from dcdata.processor import get_chained_processor, load_data
from dcdata.contribution.sources.crp import CYCLES, FILE_TYPES
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE
from crp_denormalize import *

### Filters

class RecipCodeFilter(Filter):
    def __init__(self):
        super(RecipCodeFilter, self).__init__()
    def process_record(self, record):
        if 'recip_id' in record and record['recip_id'].startswith('N'):
            if record['recip_code']:
                recip_code = record['recip_code'].strip().upper()
                record['recipient_party'] = recip_code[0]
                record['seat_result'] = recip_code[1] if recip_code[1] in ('W','L') else None
        return record

# this list was built by searching for the most frequent organization names in the unfiltered
# contribution data. I went through all organization names with at least 200 entries and entered
# all of the names that weren't organziations. -epg
disallowed_orgnames = set(['retired', 'homemaker', 'attorney', '[24i contribution]', 'self-employed', 
                          'physician', 'self', 'information requested', 'self employed', '[24t contribution]', 
                          'consultant', 'investor', '[candidate contribution]', 'n/a', 'farmer', 'real estate', 
                          'none', 'writer', 'dentist', 'info requested', 'business owner', 'accountant', 
                          'artist', 'rancher', 'student', 'realtor', 'investments', 'real estate developer', 
                          'unemployed', 'requested', 'owner', 'developer', 'businessman', 'contractor', 
                          'president', 'engineer', 'n', 'psychologist', 'real estate broker', 'executive', 
                          'private investor', 'architect', 'sales', 'real estate investor', 'selfemployed', 
                          'philanthropist', 'not employed', 'author', 'builder', 'insurance agent', 'volunteer', 
                          'construction', 'insurance', 'entrepreneur', 'lobbyist', 'ceo', 'n.a', 'actor', 
                          'photographer', 'musician', 'interior designer', 'restaurant owner', 'teacher', 
                          'designer', 'surgeon', 'social worker', 'veterinarian', 'psychiatrist', 'chiropractor', 
                          'auto dealer', 'small business owner', 'optometrist', 'producer', 'business', 
                          '.information requested', 'financial advisor', 'pharmacist', 'psychotherapist', 
                          'manager', 'management consultant', 'general contractor', 'finance', 'orthodontist', 
                          'actress', 'n.a.', 'restauranteur', 'property management', 'home builder', 'oil & gas', 
                          'real estate investments', 'geologist', 'professor', 'farming', 'real estate agent', 
                          'na', 'financial planner', 'community volunteer', 'property manager', 'political consultant', 
                          'public relations', 'business consultant', 'publisher', 'insurance broker', 'educator', 
                          'nurse', 'orthopedic surgeon', 'editor', 'marketing', 'dairy farmer', 'investment advisor', 
                          'freelance writer', 'investment banker', 'trader', 'computer consultant', 'banker', 
                          'oral surgeon', 'business executive', 'unknown', 'civic volunteer', 'filmmaker', 'economist'])


class OrganizationFilter(Filter):
    def process_record(self, record):
        orgname = record.get('org_name', '').strip()
        # disabling the orgname fallbacks--we want to be able to rely on the orgname being the human-verified name
#        if not orgname or orgname.lower() in disallowed_orgnames:
#            orgname = record.get('emp_ef', '').strip()
#            if (not orgname or orgname.lower() in disallowed_orgnames) and '/' in record.get('fec_occ_emp',''):
#                (emp, occ) = record.get('fec_occ_emp','').split('/', 1)
#                orgname = emp.strip()
        record['organization_name'] = orgname if orgname and orgname.lower() not in disallowed_orgnames else None
        return record


class CommitteeFilter(Filter):
    def __init__(self, committees):
        super(CommitteeFilter, self).__init__()
        self._committees = committees
    def process_record(self, record):
        cmte_id = record['cmte_id'].upper()
        committee = self._committees.get('%s:%s' % (record['cycle'], cmte_id), None)
        if committee:
            record['committee_name'] = committee['pac_short']
            record['committee_party'] = committee['party']
        return record
        

class RecipientFilter(Filter):
    def __init__(self, candidates, committees):
        super(RecipientFilter, self).__init__()
        self._candidates = candidates
        self._committees = committees
    def process_record(self, record):
        recip_id = record.get('recip_id','').upper()
        if recip_id.startswith('N'):
            recipient = self._candidates.get('%s:%s' % (record['cycle'], recip_id), None)
            self.load_candidate(recipient, record)
        else:
            recipient = self._committees.get('%s:%s' % (record['cycle'], recip_id), None)
            self.load_committee(recipient, record)
        return record
    def load_candidate(self, candidate, record):
        if candidate:
            record['recipient_name'] = candidate['first_last_p']
            record['recipient_party'] = candidate['party']
            record['recipient_type'] = 'politician'
            record['seat_status'] = candidate['crp_ico']
            seat = candidate['dist_id_run_for'].upper()
            if len(seat) == 4:
                if seat == 'PRES':
                    record['seat'] = 'federal:president'
                else:
                    if seat[2] == 'S':
                        record['seat'] = 'federal:senate'
                    else:
                        record['seat'] = 'federal:house'
                        record['district'] = "%s-%s" % (seat[:2], seat[2:])
    def load_committee(self, committee, record):
        if committee:
            record['recipient_name'] = committee['pac_short']
            record['recipient_party'] = committee['party']
            record['recipient_type'] = 'committee'
            cmte_id = record['cmte_id'].upper()
            recip_id = committee.get('recip_id', '').upper() 
            if cmte_id == record['recip_id'].upper() and cmte_id != recip_id:
                print "!!!!  loading committee recipient"
                candidate = self._candidates.get('%s:%s' % (record['cycle'], recip_id), None)
                self.load_candidate(candidate, record)



class CRPDenormalizeIndividual(CRPDenormalizeBase):

    @staticmethod
    def get_record_processor(catcodes, candidates, committees):
        return get_chained_processor(
                # broken at the moment--can't use anything deriving from YieldFilter
                #FieldCountValidator(len(FILE_TYPES['indivs'])),
        
                # transaction filters
                FieldAdder('transaction_namespace', CRP_TRANSACTION_NAMESPACE),
                FieldMerger({'transaction_id': ('cycle','fec_trans_id')}, lambda cycle, fecid: '%s:%s' % (cycle, fecid), keep_fields=True),
                FieldMerger({'transaction_type': ('type',)}, lambda t: t.strip().lower() if t else '', keep_fields=True),
        
                # filing reference ID
                FieldRenamer({'filing_id': 'microfilm'}),
        
                # date stamp
                FieldModifier('date', parse_date_iso),
        
                # rename contributor, organization, and parent_organization fields
                FieldRenamer({'contributor_name': 'contrib',
                          'parent_organization_name': 'ult_org',}),
         
                RecipientFilter(candidates, committees),
                CommitteeFilter(committees),
                OrganizationFilter(),
        
                # create URNs
                FieldRenamer({'contributor_ext_id': 'contrib_id', 'recipient_ext_id': 'recip_id', 'committee_ext_id': 'cmte_id'}),
                              
                # recip code filter
                RecipCodeFilter(),  # recipient party
                                # seat result
        
                # address and gender fields
                FieldRenamer({'contributor_address': 'street',
                          'contributor_city': 'city',
                          'contributor_state': 'state',
                          'contributor_zipcode': 'zipcode',
                          'contributor_gender': 'gender'}),
                FieldModifier('contributor_state', lambda s: s.upper() if s else None),
                FieldModifier('contributor_gender', lambda s: s.upper() if s else None),
        
                # employer/occupation filter
                FECOccupationFilter(),
        
                # catcode
                CatCodeFilter('contributor', catcodes),
        
                # add static fields
                FieldAdder('contributor_type', 'individual'),
                FieldAdder('is_amendment', False),
                FieldAdder('election_type', 'G'),
        
                # filter through spec
                SpecFilter(SPEC))
        
    
    def denormalize(self, data_path, cycles, catcodes, candidates, committees):
        record_processor = self.get_record_processor(catcodes, candidates, committees)   
           
        for cycle in cycles:
            in_path = os.path.join(data_path, 'raw', 'crp', 'indivs%s.csv' % cycle)
            infile = open(in_path, 'r')
            out_path = os.path.join(data_path, 'denormalized', 'denorm_indivs.%s.csv' % cycle)
            outfile = open(out_path, 'w')
    
            sys.stdout.write('Reading from %s, writing to %s...\n' % (in_path, out_path))
    
            input_source = CSVSource(infile, fieldnames=FILE_TYPES['indivs'])
            output_func = CSVEmitter(outfile, fieldnames=FIELDNAMES).process_record
    
            load_data(input_source, record_processor, output_func)
       
       
Command = CRPDenormalizeIndividual         
    