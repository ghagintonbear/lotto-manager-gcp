import logging
from datetime import date

from manager import run_manager_between, run_manager, produce_cumulative_report, get_selected_numbers

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")

if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    selected_numbers = get_selected_numbers()

    # run_manager(base_url, selected_numbers)
    # run_manager_between(base_url, selected_numbers, date(2020, 6, 27), date(2020, 12, 20))

    # run_manager_between(base_url, selected_numbers, date(2020, 6, 27), date(2020, 10, 20))
    # selected_numbers = selected_numbers[selected_numbers['Name'] != 'Ole']
    # run_manager_between(base_url, selected_numbers, date(2020, 10, 24), date(2020, 12, 20))

    # produce_cumulative_report()

    pass
