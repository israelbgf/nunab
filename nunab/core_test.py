from datetime import date, timedelta, datetime
from unittest.case import TestCase

from core import NubankTransaction, YNABTransaction, find_nubank_changes_that_needs_to_be_imported_to_ynab, \
    convert_nubank_to_yanb

YESTERDAY = date.today() - timedelta(days=1)
TOMORROW = date.today() + timedelta(days=1)


class FindNubankChangesThatNeedsToBeImportedToYnabTests(TestCase):

    def test_all_changes_from_nubank_when_nothing_from_ynab(self):
        ynab_data = []
        nubank_data = [NubankTransaction('5c4a3f30'), NubankTransaction('40370dcb')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data, (YESTERDAY, TOMORROW))

        self.assertEqual(nubank_data, result)

    def test_no_changes_when_ynab_already_have_record_with_matching_description(self):
        ynab_data = [YNABTransaction(nubank_id='5c4a3f30')]
        nubank_data = [NubankTransaction('5c4a3f30')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data, (YESTERDAY, TOMORROW))

        self.assertEqual([], result)

    def test_changes_when_some_nubank_transactions_match_some_ynab_transactions(self):
        ynab_data = [YNABTransaction(nubank_id='5c4a3f30'), YNABTransaction(nubank_id='')]
        nubank_data = [NubankTransaction('5c4a3f30'), NubankTransaction('4b3n5c62')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data, (YESTERDAY, TOMORROW))

        self.assertEqual([NubankTransaction('4b3n5c62')], result)

    def test_no_changes_when_specified_date_range_do_not_match(self):
        ynab_data = []
        nubank_data = [
            NubankTransaction('5c4a3f30', datetime=datetime(2021, 3, 31)),
            NubankTransaction('4b3n5c62', datetime=datetime(2021, 4, 15)),
            NubankTransaction('1z7x4h05', datetime=datetime(2021, 5, 1))
        ]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(
            ynab_data, nubank_data, (date(2021, 4, 1), date(2021, 4, 30)))

        self.assertEqual([nubank_data[1]], result)


class NubankTransactionToYNABTransaction(TestCase):

    def test_simple_conversion(self):
        self.assertEqual(
            YNABTransaction('5c4a3f30', -10, 'Test #NuId:5c4a3f30', date(2021, 3, 31), None, None),
            convert_nubank_to_yanb(NubankTransaction('5c4a3f30', -10, 'Test',
                                                     type='account', datetime=datetime(2021, 3, 31, 12, 13, 14))))

    def test_use_nuconta_account_id_when_transaction_is_account_type(self):
        transaction = NubankTransaction('5c4a3f30', -10, 'Test', type='nuconta',
                                        datetime=datetime(2021, 3, 31, 12, 13, 14))
        config = {'nucontaAccountId': 12345}

        self.assertEqual(
            YNABTransaction('5c4a3f30', -10, 'Test #NuId:5c4a3f30', date(2021, 3, 31), None, 12345),
            convert_nubank_to_yanb(transaction, config)
        )

    def test_use_creditcard_account_id_when_transaction_is_account_type(self):
        transaction = NubankTransaction('5c4a3f30', -10, 'Test', type='creditcard',
                                        datetime=datetime(2021, 3, 31, 12, 13, 14))
        config = {'creditcardAccountId': 54321}

        self.assertEqual(
            YNABTransaction('5c4a3f30', -10, 'Test #NuId:5c4a3f30', date(2021, 3, 31), None, 54321),
            convert_nubank_to_yanb(transaction, config)
        )

    def test_use_category_id_when_theres_a_mapping_set(self):
        transaction = NubankTransaction('5c4a3f30', -10, 'Test', type='creditcard',
                                        datetime=datetime(2021, 3, 31, 12, 13, 14))
        config = {'categoryMapping': {'Test': 999}}

        self.assertEqual(
            YNABTransaction('5c4a3f30', -10, 'Test #NuId:5c4a3f30', date(2021, 3, 31), 999, None),
            convert_nubank_to_yanb(transaction, config)
        )
