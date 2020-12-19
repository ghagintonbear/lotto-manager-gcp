from datetime import datetime

import pandas as pd

from manager.scrape_results import scrape_historical_results, extract_draw_result, scrape_prize_breakdown
from manager.check_matches import collect_winning_numbers, check_matches_on_selected


def run_manager(draw_date: datetime, base_url: str, selected: pd.DataFrame):
    draw_result, prize_breakdown = get_draw_information(base_url, draw_date)
    winning_numbers = collect_winning_numbers(draw_result)

    results = check_matches_on_selected(selected, winning_numbers, prize_breakdown)

    return results


def get_draw_information(base_url: str, draw_date: datetime) -> (dict, dict):
    historical_data = scrape_historical_results(base_url)
    draw_result = extract_draw_result(draw_date, historical_data)
    prize_breakdown = scrape_prize_breakdown(base_url, draw_result['DrawNumber'])
    return draw_result, prize_breakdown
