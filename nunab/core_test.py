from datetime import datetime, date
from unittest.case import TestCase

from core import NubankTransaction, YNABTransaction, find_nubank_changes_that_needs_to_be_imported_to_ynab, \
    dict_to_nubank_transaction, dict_to_ynab_transaction


class FindNubankChangesThatNeedsToBeImportedToYnabTests(TestCase):

    def test_all_changes_from_nubank_when_nothing_from_ynab(self):
        ynab_data = []
        nubank_data = [NubankTransaction('5c4a3f30'), NubankTransaction('40370dcb')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data)

        self.assertEqual(nubank_data, result)

    def test_no_changes_when_ynab_already_have_record_with_matching_description(self):
        ynab_data = [YNABTransaction(nubank_id='5c4a3f30')]
        nubank_data = [NubankTransaction('5c4a3f30')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data)

        self.assertEqual([], result)

    def test_changes_when_some_nubank_transactions_match_some_ynab_transactions(self):
        ynab_data = [YNABTransaction(nubank_id='5c4a3f30'), YNABTransaction(nubank_id='')]
        nubank_data = [NubankTransaction('5c4a3f30'), NubankTransaction('4b3n5c62')]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_data, nubank_data)

        self.assertEqual([NubankTransaction('4b3n5c62')], result)

    def test_no_changes_when_specified_date_range_do_not_match(self):
        ynab_data = []
        nubank_data = [
            NubankTransaction('5c4a3f30', datetime=datetime(2021, 3, 31)),
            NubankTransaction('4b3n5c62', datetime=datetime(2021, 4, 15)),
            NubankTransaction('1z7x4h05', datetime=datetime(2021, 5, 1))
        ]

        result = find_nubank_changes_that_needs_to_be_imported_to_ynab(
            ynab_data, nubank_data,
            valid_range=(date(2021, 4, 1), date(2021, 4, 30)))

        self.assertEqual([nubank_data[1]], result)


class DictToYnabTransactionTests(TestCase):

    def test_nubank_id_is_empty_when_memo_do_not_contains_previously_saved_nubank_id(self):
        self.assertEqual(YNABTransaction(nubank_id=''), dict_to_ynab_transaction({"memo": "BRAVOS GRIL"}))

    def test_nubank_id_parsed_when_memo_contains_previously_saved_nubank_id(self):
        self.assertEqual(YNABTransaction(nubank_id='12345'), dict_to_ynab_transaction({"memo": "BRAVOS #GRIL "
                                                                                               "#NuId:12345"}))

    def test_nubank_id_is_empty_when_memo_is_none(self):
        self.assertEqual(YNABTransaction(), dict_to_ynab_transaction({"memo": None}))


class CreditCardDictToNuBankTransactionTests(TestCase):

    def test_parse_transaction_from_dictionary(self):
        self.assertEqual(
            NubankTransaction(
                id='5a7b096d',
                amount=1000,
                description='Pappos',
                type='creditcard',
                datetime=datetime(2018, 2, 7, 14, 13, 1)),

            dict_to_nubank_transaction({'_links': {'self': {
                'href': 'https://api.com/api/transactions/5a7b096d-xxxx-xxxx-xxxx-6e4244004798'}},
                'amount': 1000,
                'category': 'transaction',
                'description': 'Pappos',
                'details': {'lat': -26.2542084,
                            'lon': -48.8492242,
                            'subcategory': 'card_present'},
                'id': '5a7b096d-a251-xxxx-xxxx-xxxxxxxxxxxx',
                'time': '2018-02-07T14:13:01Z',
                'title': 'restaurante'}))


class AccountDictToNuBankTransactionTests(TestCase):

    def test_parse_deposit_dict(self):
        self.assertEqual(
            NubankTransaction(
                id='606f2b6e',
                amount=250000,
                description='Depósito de Tinhoso Fonseca',
                type='account',
                datetime=datetime(2021, 4, 8)),

            dict_to_nubank_transaction({
                "id": "606f2b6e-xxxx-xxxx-xxxx-8dd05ed3379d",
                "__typename": "TransferInEvent",
                "title": "Transfer\u00eancia recebida",
                "detail": "R$\u00a02.500,00",
                "postDate": "2021-04-08",
                "amount": 2500.0,
                "originAccount": {
                    "name": "Tinhoso Fonseca"
                }}))

    def test_parse_unknown_source_deposit_dict(self):
        self.assertEqual(
            NubankTransaction(
                id='606f2b6e',
                amount=250000,
                description='Transfer\u00eancia recebida',
                type='account',
                datetime=datetime(2021, 4, 8)),

            dict_to_nubank_transaction({
                "id": "606f2b6e-xxxx-xxxx-xxxx-8dd05ed3379d",
                "__typename": "TransferInEvent",
                "title": "Transfer\u00eancia recebida",
                "detail": "R$\u00a02.500,00",
                "postDate": "2021-04-08",
                "amount": 2500.0,
                "originAccount": None}))

    def test_parse_transfer_dict(self):
        self.assertEqual(
            NubankTransaction(
                id='756f2b6e',
                amount=531,
                description='Transferência para Juca Silva',
                type='account',
                datetime=datetime(2021, 4, 8)),

            dict_to_nubank_transaction({
                "id": "756f2b6e-xxxx-xxxx-xxxx-8dd05ed3379d",
                "__typename": "TransferOutEvent",
                "title": "Transfer\u00eancia enviada",
                "detail": "Juca Silva - R$\u00a05,31",
                "postDate": "2021-04-08",
                "amount": 5.31,
                "destinationAccount": {
                    "name": "Juca Silva"
                }
            }, ))

    def test_parse_barcode_dict(self):
        self.assertEqual(
            NubankTransaction(
                id='5ecf3833',
                amount=4497,
                description='DARF IRRF',
                type='account',
                datetime=datetime(2020, 5, 28)),

            dict_to_nubank_transaction({
                "id": "5ecf3833-xxxx-xxxx-xxxx-7bb506717ce0",
                "__typename": "BarcodePaymentEvent",
                "title": "Pagamento efetuado",
                "detail": "DARF IRRF",
                "postDate": "2020-05-28",
                "amount": 44.97
            }))
