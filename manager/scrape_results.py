import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bSoup
import pandas as pd

logging.basicConfig(format="[%(filename)s: %(funcName)s] %(message)s")


def scrape_historical_results(base_url: str) -> pd.DataFrame:
    draw_history_url_path = base_url + '/results/euromillions/draw-history'

    draw_history_page = requests.get(draw_history_url_path)
    draw_history_soup = bSoup(draw_history_page.content, 'html.parser')

    link_to_csv = base_url + draw_history_soup.find(id='download_history_action').get('href')

    try:
        historical_results = pd.read_csv(link_to_csv)
    except Exception as E:
        logging.error(f'Failed to read data from: "{link_to_csv}"')
        logging.error(f'Caused by: {E}')
        raise E

    return historical_results


def extract_draw_result(draw_date: datetime, hist_results: pd.DataFrame) -> dict:
    hist_results['DrawDate'] = pd.to_datetime(hist_results['DrawDate'], format='%d-%b-%Y')
    draw_date_mask = hist_results['DrawDate'] == draw_date

    if draw_date_mask.sum() == 0:
        raise Exception(f'Selected draw_date: "{draw_date: %d-%m-%Y}" not in hist_results["DrawDate"]')
    if draw_date_mask.sum() > 1:
        raise Exception(f'Selected draw_date: "{draw_date: %d-%m-%Y}" maps to many in hist_results["DrawDate"]')

    draw_result = hist_results[draw_date_mask].to_dict('records')[0]

    return draw_result


if __name__ == '__main__':
    base_url = 'https://www.national-lottery.co.uk'
    historical_data = scrape_historical_results(base_url)
    draw_result = extract_draw_result(datetime(2020, 12, 15), historical_data)
    print(draw_result)
