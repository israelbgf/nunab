import json
import os

import requests
from pynubank import Nubank

from core import dict_to_nubank_transaction, dict_to_ynab_transaction

NUBANK_CPF = os.environ.get('NUBANK_CPF')
NUBANK_PASSWORD = os.environ.get('NUBANK_PASSWORD')
NUBANK_CERT = os.environ.get('NUBANK_CERT')
YNAB_API_TOKEN = os.environ.get('YNAB_API_TOKEN')
YNAB_BUDGET_ID = os.environ.get('YNAB_BUDGET_ID')


def download_ynab_transactions(since, dest):
    response = requests.get(
        f'https://api.youneedabudget.com/v1/budgets/{YNAB_BUDGET_ID}/transactions?since_date={since}',
        headers={
            'Authorization': f'Bearer {YNAB_API_TOKEN}',
            'accept': 'application/json'
        })

    with open(dest, 'wb') as output:
        output.write(response.content)


def get_ynab_transactions():
    with open('transactions.ynab.json') as input:
        return map(dict_to_ynab_transaction, json.load(input)['data']['transactions'])


def download_nubank_transactions():
    nu = Nubank()
    nu.authenticate_with_cert(NUBANK_CPF, NUBANK_PASSWORD, NUBANK_CERT)
    statements = nu.get_card_statements()
    with open('creditcard_transactions.nubank.json', 'w') as output:
        json.dump(statements, output)

    statements = nu.get_account_statements()
    with open('account_transactions.nubank.json', 'w') as output:
        json.dump(statements, output)


def get_nubank_transactions():
    transactions = []
    with open('creditcard_transactions.nubank.json', 'rb') as input:
        transactions.extend(map(dict_to_nubank_transaction, json.load(input)))
    with open('account_transactions.nubank.json', 'rb') as input:
        transactions.extend(map(dict_to_nubank_transaction, json.load(input)))
    return transactions


def send_changes_to_ynab(changes):
    sum = 0
    for change in changes:
        sum += change.amount
        print(change)
    print(sum)
