import sys
from datetime import date, timedelta

import yaml

from core import find_nubank_changes_that_needs_to_be_imported_to_ynab, convert_nubank_to_yanb
from gateways import *

NUNAB_CONFIG = yaml.safe_load(open('../config.production.yaml'))
START_DATE = date(2021, 5, 1)


def sync_ynab_with_nubank():
    ynab = get_ynab_transactions()
    nubank = get_nubank_transactions()
    transactions = find_nubank_changes_that_needs_to_be_imported_to_ynab(ynab, nubank, valid_range=(START_DATE,
                                                                                                    date(2022, 5, 1)))

    send_changes_to_ynab(list(map(lambda x: convert_nubank_to_yanb(x, NUNAB_CONFIG), transactions)))


if __name__ == '__main__':
    input = sys.argv[1]

    if input == 'download-nubank-data':
        download_nubank_transactions()
    if input == 'sync-ynab':
        max_date_to_avoid_large_response = START_DATE
        print(f'Syncing data since {max_date_to_avoid_large_response}')
        download_ynab_transactions(since=max_date_to_avoid_large_response, dest='transactions.ynab.json')
        sync_ynab_with_nubank()
    if input == 'debug-ynab':
        list_ynab_categories()
