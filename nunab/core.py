import re
from dataclasses import dataclass
from datetime import datetime, date


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


def dict_to_ynab_transaction(dictionary):
    nubank_id = ''

    matches = re.findall("#NuId:(.*)", dictionary['memo'] or '')
    if matches:
        nubank_id = matches[-1]

    return YNABTransaction(
        nubank_id,
    )