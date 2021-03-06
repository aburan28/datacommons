
from datetime import date
from dcapi.contributions.handlers import filter_contributions
from dcdata.contribution.models import Contribution, \
    UNITTEST_TRANSACTION_NAMESPACE
from dcdata.models import Import
from django.db import connection
from django.test import TestCase
from nose.plugins.skip import SkipTest


class Tests(TestCase):           
    
    def create_entities(self):
        self.create_contribution(contributor_name='1234')
        self.create_contribution(organization_name='1234')
        self.create_contribution(parent_organization_name='5678')
        self.create_contribution(recipient_name='abcd')
        self.create_contribution(recipient_name='efgh')
        self.create_contribution(committee_name='efgh')

    def assert_num_results(self, expected_num, request):
        self.assertEqual(expected_num, filter_contributions(request).count())

    def create_contribution(self, **kwargs):
        c = Contribution(**kwargs)
        if 'cycle' not in kwargs:
            c.cycle='09'
        c.transaction_namespace=UNITTEST_TRANSACTION_NAMESPACE
        c.import_reference=self.import_
        c.save()

    def setUp(self):
        self.import_ = Import()
        self.import_.save()

        cursor = connection.cursor()
        for command in open( 'dcdata/scripts/contribution_name_indexes.sql', 'r'):
            if command.strip() and not command.startswith('--'):
                cursor.execute(command)

    def test_date(self):
        self.create_contribution(date=date(1999,12,25))
        self.create_contribution(date=date(1999,12,31))
        self.create_contribution(date=date(2000,1,1))

        self.assert_num_results(0, {'date': ">|2001-01-01"})
        self.assert_num_results(1, {'date': "><|1999-12-24|1999-12-26"})
        self.assert_num_results(2, {'date': "<|1999-12-31"})
        self.assert_num_results(3, {'date': ">|1980-01-01"})


    def test_contributor(self):
        self.create_entities()

        self.assert_num_results(0, {'contributor_ft': "abcd"})
        self.assert_num_results(2, {'contributor_ft': "1234"})
        self.assert_num_results(3, {'contributor_ft': "1234|5678"})

    def test_recipient(self):
        self.create_entities()

        self.assert_num_results(0, {'recipient_ft': "1234"})
        self.assert_num_results(1, {'recipient_ft': "abcd"})
        self.assert_num_results(2, {'recipient_ft': "abcd|efgh"})
        self.assert_num_results(2, {'recipient_ft': "0000|abcd|efgh"})

    def test_amount(self):
        self.create_contribution(amount=100)
        self.create_contribution(amount=500)
        self.create_contribution(amount=800)

        self.assert_num_results(0, {'amount': ">|1000"})
        self.assert_num_results(0, {'amount': "<|50"})
        self.assert_num_results(1, {'amount': ">|600"})
        self.assert_num_results(2, {'amount': "<|500"})
        self.assert_num_results(3, {'amount': "><|100|800"})

    def test_cycle(self):
        self.create_contribution(cycle=02)
        self.create_contribution(cycle=04)
        self.create_contribution(cycle=04)

        self.assert_num_results(0, {'cycle': "08"})
        self.assert_num_results(1, {'cycle': "02"})
        self.assert_num_results(2, {'cycle': "04"})

    def test_state(self):
        self.create_contribution(contributor_state='CA')
        self.create_contribution(contributor_state='OR')
        self.create_contribution(contributor_state='OR')

        self.assert_num_results(0, {'contributor_state': "WA"})
        self.assert_num_results(1, {'contributor_state': "CA"})
        self.assert_num_results(2, {'contributor_state': "OR"})

    def test_conjunctions(self):
        self.create_contribution(contributor_name='apple', contributor_state="WA", amount=1000)
        self.create_contribution(contributor_name='apple sauce', contributor_state="WA", amount=100)

        self.assert_num_results(0, {'contributor_state': "CA", 'amount': ">|500"})
        self.assert_num_results(1, {'contributor_state': "WA", 'amount': ">|500"})
        self.assert_num_results(1, {'amount': ">|500"})

        self.assert_num_results(2, {'contributor_ft': 'apple'})
        self.assert_num_results(1, {'contributor_ft': 'apple', 'amount': '>|500'})
        self.assert_num_results(0, {'contributor_ft': 'sauce', 'amount': '>|500'})

    def test_full_text(self):
        self.create_contribution(contributor_name="Joe Smith")

        self.assert_num_results(0, {'contributor_ft': 'Bruce'})
        self.assert_num_results(0, {'organization_ft': 'Smith'})
        self.assert_num_results(0, {'contributor_ft': 'Bob Smith'})
        self.assert_num_results(1, {'contributor_ft': 'Joe'})
        self.assert_num_results(1, {'contributor_ft': 'Smith'})
        self.assert_num_results(1, {'contributor_ft': 'Joe Smith'})
        self.assert_num_results(1, {'contributor_ft': 'Smith Joe'})
        self.assert_num_results(1, {'contributor_ft': 'joe smith'})

        self.create_contribution(recipient_name="John Adams")
        self.create_contribution(recipient_name="Barry Adams")

        self.assert_num_results(2, {'recipient_ft': 'adams'})
        self.assert_num_results(1, {'recipient_ft': 'john'})
        self.assert_num_results(1, {'recipient_ft': 'barry'})

        self.create_contribution(committee_name='Committee to Commit')

        self.assert_num_results(1, {'committee_ft': 'to'})
        self.assert_num_results(1, {'committee_ft': 'commit'})

        self.create_contribution(contributor_employer='Meany & Sons')
        self.create_contribution(organization_name="Jason Q. Meany")
        self.create_contribution(parent_organization_name="Jason Q. Meany Sr.")

        self.assert_num_results(3, {'organization_ft': 'Meany'})
        self.assert_num_results(1, {'organization_ft': 'Meany Sr.'})
        self.assert_num_results(1, {'organization_ft': 'Sons'})

    def test_stop_words(self):
        self.create_contribution(contributor_name='Apple Association Inc')

        self.assert_num_results(0, {'contributor_ft': 'association'})
        self.assert_num_results(0, {'contributor_ft': 'inc'})
        self.assert_num_results(0, {'contributor_ft': 'assoc'})

        self.assert_num_results(1, {'contributor_ft': 'apple'})
        self.assert_num_results(1, {'contributor_ft': 'apple association inc'})
        self.assert_num_results(1, {'contributor_ft': 'apple corp'})

    def test_contributor_search(self):
        self.create_contribution(contributor_name='apple')
        self.create_contribution(contributor_employer='apple')
        self.create_contribution(organization_name='apple')
        self.create_contribution(parent_organization_name='apple')

        self.assert_num_results(4, {'contributor_ft': 'apple'})
        self.assert_num_results(3, {'organization_ft': 'apple'})

    def test_multiple_ft(self):
        """ See ticket #196. """

        self.create_contribution(contributor_name='Billy Bob')
        self.create_contribution(contributor_name='Marry Sue')

        self.assert_num_results(1, {'contributor_ft': 'billy bob'})
        self.assert_num_results(1, {'contributor_ft': 'marry sue'})

        self.assert_num_results(0, {'contributor_ft': 'billy lee'})
        self.assert_num_results(0, {'contributor_ft': 'billy lee|marry sue lee'})
        self.assert_num_results(1, {'contributor_ft': 'billy lee|marry sue'})
        self.assert_num_results(2, {'contributor_ft': 'billy|marry'})
        self.assert_num_results(2, {'contributor_ft': 'billy bob|marry'})
        self.assert_num_results(2, {'contributor_ft': 'billy bob|marry sue'})

    def test_punctuation_ft(self):
        self.create_contribution(recipient_name='PG&E Corp')
        self.create_contribution(recipient_name='PGE Corp')
        self.create_contribution(recipient_name='PG & E Corp')
        self.create_contribution(recipient_name='PG and E Corp')

        self.assert_num_results(3, {'recipient_ft': 'pg&e'})

        # in a perfect world this would be found by the searches above,
        # but Postgres unfortunately treats the ones above as two tokens and this as one.
        self.assert_num_results(1, {'recipient_ft': 'pge'})

        # test parentheses
        self.create_contribution(recipient_name='John Doe (R)')
        self.create_contribution(recipient_name='John R James')

        self.assert_num_results(2, {'recipient_ft': 'John (R)'})
        self.assert_num_results(2, {'recipient_ft': 'John R'})

        # failing right now: 'and' should be a stop word, but isn't
        raise SkipTest
        self.assert_num_results(3, {'recipient_ft': 'pg and e'})

