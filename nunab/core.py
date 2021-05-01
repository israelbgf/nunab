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
    amount: int = 0
    description: str = ''
    date: date = None
    category_id: int = None
    account_id: int = None


def find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab_transactions: [YNABTransaction],
                                                          nubank_transactions: [NubankTransaction],
                                                          valid_range: (date, date)):
    ynab_transactions = {t.nubank_id: t for t in ynab_transactions}

    matches = []
    for transaction in nubank_transactions:
        inside_range = valid_range[0] <= transaction.datetime.date() <= valid_range[1]
        if not inside_range:
            continue

        ynab_match = ynab_transactions.get(transaction.id)
        if not ynab_match:
            matches.append(transaction)

    return matches


def convert_nubank_to_yanb(nubank_transaction, nunab_config=None):
    nunab_config = nunab_config or {}
    account_id = nunab_config.get(
        'creditcard_account_id' if nubank_transaction.type == 'creditcard' else 'nuconta_account_id')

    return YNABTransaction(
        nubank_transaction.id, nubank_transaction.amount, nubank_transaction.description,
        nubank_transaction.datetime.date(),
        nunab_config.get('categoryMapping', {}).get(nubank_transaction.description),
        account_id
    )