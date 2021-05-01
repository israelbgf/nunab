import json
import os
import pickle
import re
from dataclasses import dataclass
from datetime import datetime, date

import requests
from pynubank import Nubank

NUBANK_CPF = os.environ.get('NUBANK_CPF')
NUBANK_PASSWORD = os.environ.get('NUBANK_PASSWORD')
NUBANK_CERT = os.environ.get('NUBANK_CERT')

YNAB_API_TOKEN = os.environ.get('YNAB_API_TOKEN')
YNAB_BUDGET_ID = os.environ.get('YNAB_BUDGET_ID')


@dataclass
class NubankTransaction:
    id: str
    amount: int = 0
    description: str = ''
    type: str = ''
    datetime: datetime = datetime.today()


@dataclass
class YNABTransaction:
    nubank_id: str = ''


def download_nubank_transactions():
    nu = Nubank()
    nu.authenticate_with_cert(NUBANK_CPF, NUBANK_PASSWORD, NUBANK_CERT)
    statements = nu.get_card_statements()
    with open('creditcard_transactions.nubank.json', 'w') as output:
        json.dump(statements, output)

    statements = nu.get_account_statements()
    with open('account_transactions.nubank.json', 'w') as output:
        json.dump(statements, output)


def load_creditcard_data(source):
    with open(source, 'rb') as input:
        return pickle.load(input)


def download_ynab_transactions(since, dest):
    response = requests.get(
        f'https://api.youneedabudget.com/v1/budgets/{YNAB_BUDGET_ID}/transactions?since_date={since}',
        headers={
            'Authorization': f'Bearer {YNAB_API_TOKEN}',
            'accept': 'application/json'
        })

    with open(dest, 'wb') as output:
        output.write(response.content)


def find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_transactions: [YNABTransaction],
                                                          nubank_transactions: [NubankTransaction],
                                                          valid_range: (date, date) = None):
    ynab_transactions = {t.nubank_id: t for t in ynab_transactions}

    matches = []
    for transaction in nubank_transactions:
        has_range = valid_range is None
        inside_valid_range = True if has_range else valid_range[0] <= transaction.datetime.date() <= valid_range[1]
        if not inside_valid_range:
            continue

        ynab_match = ynab_transactions.get(transaction.id)
        if not ynab_match:
            matches.append(transaction)

    return matches


def dict_to_nubank_transaction(dictionary):
    type = 'account' if 'postDate' in dictionary else 'creditcard'
    id = dictionary['id'].split('-')[0]

    if type == 'account':
        originAccount = dictionary.get('originAccount', {}).get('name')
        destinationAccount = dictionary.get('destinationAccount', {}).get('name')
        description = dictionary.get('detail')

        if originAccount:
            description = 'Depósito de {}'.format(originAccount)
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


def get_ynab_transactions():
    with open('transactions.ynab.json') as input:
        return map(dict_to_ynab_transaction, json.load(input)['data']['transactions'])


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


def send_changes_to_ynab(changes):
    sum = 0
    for change in changes:
        sum += change.amount
        print(change)
    print(sum)


def sync_ynab_with_nubank():
    ynab = get_ynab_transactions()
    nubank = get_nubank_transactions()
    changes = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab, nubank, valid_range=(date(2021, 4, 22),
                                                                                               date(2021, 4, 30)))
    send_changes_to_ynab(changes)


if __name__ == '__main__':
    print(get_nubank_transactions())
    # sync_ynab_with_nubank()
    # download_nubank_transactions()
    # download_ynab_transactions(since='2021-04-01', dest='transactions.ynab.json')
    # sync_ynab_with_nubank()
    # pprint(pickle.load(open('transactions.nubank.pickle', 'rb')))
    # pprint(pickle.load(open('transactions.ynab')))
