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


def dict_to_ynab_transaction(dictionary):
    nubank_id = ''

    matches = re.findall("#NuId:(.*)", dictionary['memo'] or '')
    if matches:
        nubank_id = matches[-1]

    return YNABTransaction(
        nubank_id,
    )


def dict_to_nubank_transaction(dictionary):
    type = 'nuconta' if 'postDate' in dictionary else 'creditcard'
    id = dictionary['id'].split('-')[-1]

    if type == 'nuconta':
        event_type = dictionary.get('__typename')
        originAccount = dictionary.get('originAccount', {})
        destinationAccount = dictionary.get('destinationAccount', {}).get('name')
        description = dictionary.get('detail')

        if originAccount:
            description = 'Depósito de {}'.format(originAccount.get('name'))
        elif originAccount is None:
            description = dictionary.get('title')
        if destinationAccount:
            description = 'Transferência para {}'.format(destinationAccount)
        if event_type == 'DebitPurchaseEvent':
            description = description.split(' - ')[0]

        return NubankTransaction(
            id,
            int(dictionary['amount'] * 100 * (1 if 'TransferIn' in event_type else -1)),
            description,
            type,
            datetime.strptime(dictionary['postDate'], "%Y-%m-%d"),
        )
    else:
        return NubankTransaction(
            id,
            dictionary['amount'] * -1,
            dictionary['description'],
            type,
            datetime.strptime(dictionary['time'], "%Y-%m-%dT%H:%M:%SZ"),
        )


def send_changes_to_ynab_stdout(transactions):
    sum = 0
    for t in transactions:
        sum += t.amount
        print(t)
    print('Sum:', sum)


def list_ynab_categories():
    response = requests.get(
        f'https://api.youneedabudget.com/v1/budgets/{YNAB_BUDGET_ID}/categories',
        headers={
            'Authorization': f'Bearer {YNAB_API_TOKEN}',
            'accept': 'application/json'
        })

    categories = json.loads(response.content)
    for category_group in categories['data']['category_groups']:
        for category in category_group['categories']:
            if not category['deleted']:
                print(category['name'], '||', category['id'])


def send_changes_to_ynab_real(transactions: [YNABTransaction]):
    response = requests.post(
        f'https://api.youneedabudget.com/v1/budgets/{YNAB_BUDGET_ID}/transactions',
        json={
            'transactions': [{
                "account_id": t.account_id,
                "amount": t.amount * 10,  # For some reason, the API needs one extra 0.
                "category_id": t.category_id,
                "date": t.date.strftime("%Y-%m-%d"),
                "memo": t.description
            } for t in transactions]},
        headers={
            'Authorization': f'Bearer {YNAB_API_TOKEN}',
            'accept': 'application/json'
        })

    if response.status_code != 201:
        raise Exception(response.content)


def send_changes_to_ynab(transactions, dryrun):
    if dryrun:
        send_changes_to_ynab_stdout(transactions)
    else:
        send_changes_to_ynab_real(transactions)
