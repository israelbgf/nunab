import json
import os
import re
from datetime import datetime

import requests
from pynubank import Nubank

from core import YNABTransaction, NubankTransaction

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
        return list(map(dict_to_ynab_transaction, json.load(input)['data']['transactions']))


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


def dict_to_ynab_transaction(dictionary):
    nubank_id = ''

    matches = re.findall("#NuId:(.*)", dictionary['memo'] or '')
    if matches:
        nubank_id = matches[-1]

    return YNABTransaction(
        nubank_id,
    )


def dict_to_nubank_transaction(dictionary):
    type = 'account' if 'postDate' in dictionary else 'creditcard'
    id = dictionary['id'].split('-')[0]

    if type == 'account':
        originAccount = dictionary.get('originAccount', {})
        destinationAccount = dictionary.get('destinationAccount', {}).get('name')
        description = dictionary.get('detail')

        if originAccount:
            description = 'Depósito de {}'.format(originAccount.get('name'))
        if originAccount is None:
            description = dictionary.get('title')

        if destinationAccount:
            description = 'Transferência para {}'.format(destinationAccount)

        return NubankTransaction(
            id,
            int(dictionary['amount'] * 100),
            description,
            type,
            datetime.strptime(dictionary['postDate'], "%Y-%m-%d"),
        )
    else:
        return NubankTransaction(
            id,
            dictionary['amount'],
            dictionary['description'],
            type,
            datetime.strptime(dictionary['time'], "%Y-%m-%dT%H:%M:%SZ"),
        )
