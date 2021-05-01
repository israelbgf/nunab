from datetime import date

from core import find_nubank_changes_that_needs_to_be_imported_to_ynab
from gateways import get_ynab_transactions, get_nubank_transactions, send_changes_to_ynab


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
