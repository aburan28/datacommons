
from dcdata.contribution.models import CRP_TRANSACTION_NAMESPACE, \
    NIMSP_TRANSACTION_NAMESPACE
from dcentity.entity import build_entity
from django.core.management.base import BaseCommand
import csv
import os
import sys
import traceback

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'




def build_recipients(csv_rows):
    for (name,id,namespace) in csv.reader(csv_rows):
        try:
            print 'Generating entity for %s, %s, %s' % (name, namespace, id)
            name = name.strip().decode('utf8', 'replace')
            id = id.strip()
            namespace = namespace.strip()
                
            if id:
                if namespace == NIMSP_TRANSACTION_NAMESPACE:
                    attr_namespace = 'urn:nimsp:recipient'
                elif namespace == CRP_TRANSACTION_NAMESPACE:
                    attr_namespace = 'urn:crp:recipient'
                else:
                    raise Exception('Unknown namespace: %s' % namespace)
                attributes = [(attr_namespace, id)]
            
            build_entity(name, 'recipient', attributes)
            
        except:
            traceback.print_exception(*sys.exc_info())
            print "!!!!! Skipping Entity: %s !!!!!" % name
        finally:
            sys.stderr.flush()
            sys.stdout.flush()
            

class Command(BaseCommand):
    def handle(self, input_path, **args):
        build_recipients(open(input_path, 'r'))
    
    