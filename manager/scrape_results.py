import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup as bSoup
import pandas as pd


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
        raise Exception(f'Selected draw_date: "{draw_date:%d-%m-%Y}" not in hist_results["DrawDate"]')
    if draw_date_mask.sum() > 1:
        raise Exception(f'Selected draw_date: "{draw_date:%d-%m-%Y}" maps to many in hist_results["DrawDate"]')

    draw_result = hist_results[draw_date_mask].to_dict('records')[0]

    return draw_result


def scrape_prize_breakdown(base_url: str, draw_number: int) -> dict:
    breakdown_url_ext = f'/results/euromillions/draw-history/prize-breakdown/{draw_number}'
    breakdown_page = requests.get(base_url + breakdown_url_ext)
    breakdown_soup = bSoup(breakdown_page.content, 'html.parser')
    prize_breakdown = {}
    for table in breakdown_soup.find_all('table'):
        if table.get('summary').startswith('Table displaying prize breakdown'):
            match_type = None
            prize = None
            for tag in table.find_all('td'):
                if tag.get('data-th') == 'No. of matches':
                    match_type = tag.text.strip()
                if tag.get('data-th') == 'Prize per UK winner':
                    prize = tag.text.strip()
                if match_type is not None and prize is not None:
                    prize_breakdown[match_type] = prize
                    match_type = None
                    prize = None

    return prize_breakdown
