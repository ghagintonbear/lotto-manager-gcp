import logging
from datetime import datetime

import pandas as pd

from manager import run_manager

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")

if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    draw_date = datetime(2020, 12, 15)
    selected_numbers = pd.read_excel('./selected_numbers.xlsx', engine='openpyxl')

    results = run_manager(draw_date, base_url, selected_numbers)
    pass
