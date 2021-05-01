from datetime import datetime
from unittest.case import TestCase

from core import YNABTransaction, NubankTransaction
from gateways import dict_to_ynab_transaction, dict_to_nubank_transaction


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