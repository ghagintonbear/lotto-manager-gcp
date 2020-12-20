import logging
from datetime import datetime

import pandas as pd

from manager import run_manager_between

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")

if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    selected_numbers = pd.read_excel('./selected_numbers.xlsx', engine='openpyxl')

    run_manager_between(base_url, selected_numbers, datetime(2020, 6, 27), datetime(2020, 12, 20))
    pass
