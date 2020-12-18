import logging
from datetime import datetime

from manager import get_draw_information

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")

if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    draw_date = datetime(2020, 12, 15)
    draw_result, prize_breakdown = get_draw_information(base_url, draw_date)
    pass
