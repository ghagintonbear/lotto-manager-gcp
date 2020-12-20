import logging
from datetime import datetime

import pandas as pd

from manager import run_manager_between, run_manager, produce_cumulative_report

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")

if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    selected_numbers = pd.read_excel('./Selected Numbers.xlsx', engine='openpyxl')

    run_manager_between(base_url, selected_numbers, datetime(2020, 6, 27), datetime(2020, 12, 20))
    # run_manager(base_url, selected_numbers)
    produce_cumulative_report()
    pass
