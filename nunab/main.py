from datetime import date

import yaml

from core import find_nubank_changes_that_needs_to_be_imported_to_ynab, convert_nubank_to_yanb
from gateways import *

NUNAB_CONFIG = yaml.safe_load(open('../config.production.yaml'))


def sync_ynab_with_nubank():
    ynab = get_ynab_transactions()
    nubank = get_nubank_transactions()
    transactions = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab, nubank, valid_range=(date(2021, 5, 1),
                                                                                                    date(2022, 5, 1)))

    send_changes_to_ynab(list(map(lambda x: convert_nubank_to_yanb(x, NUNAB_CONFIG), transactions)), dryrun=True)


if __name__ == '__main__':
    sync_ynab_with_nubank()
    # list_ynab_categories()
    # download_nubank_transactions()
    # download_ynab_transactions(since='2021-04-01', dest='transactions.ynab.json')
