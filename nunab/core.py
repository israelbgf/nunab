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
