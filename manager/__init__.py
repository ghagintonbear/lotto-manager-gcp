from datetime import date, datetime

import pandas as pd

from manager.scrape_results import scrape_historical_results, extract_draw_result, scrape_prize_breakdown
from manager.check_matches import collect_winning_numbers, check_matches_on_selected
from manager.writer import write_result, write_cumulative_result
from manager.cumulate_results import compute_cumulated_result
from manager.tools import (
    get_last_friday_date, get_folder_name, make_results_folder, add_sum_row, assert_values_in_range
)


def run_manager(base_url: str, selected: pd.DataFrame, run_date: date = datetime.now().date()):
    draw_date, draw_date_str = get_last_friday_date(run_date)
    folder_name = get_folder_name(draw_date)
    folder_path = make_results_folder(folder_name)

    draw_result, prize_breakdown = get_draw_information(base_url, draw_date)
    winning_numbers = collect_winning_numbers(draw_result)

    results = check_matches_on_selected(selected, winning_numbers, prize_breakdown)

    write_result(folder_path=folder_path, file_name=draw_date_str, result=results,
                 draw_result=draw_result, prize_breakdown=prize_breakdown)

    return results


def get_draw_information(base_url: str, draw_date: date) -> (dict, dict):
    historical_data = scrape_historical_results(base_url)
    draw_result = extract_draw_result(draw_date, historical_data)
    prize_breakdown = scrape_prize_breakdown(base_url, draw_result['DrawNumber'])
    return draw_result, prize_breakdown


def run_manager_between(base_url: str, selected: pd.DataFrame, start: date, end: date, freq: str = '7D'):
    for run_date in pd.date_range(start, end, freq=freq):
        run_manager(base_url, selected, run_date)


def produce_cumulative_report():
    general_overview, player_breakdown = compute_cumulated_result()

    player_summary = player_breakdown.groupby('Interval', as_index=False).sum()
    player_summary = add_sum_row('Interval', player_summary)

    write_cumulative_result({
        'Player Summary': (player_summary, player_summary.dtypes[player_summary.dtypes != 'object'].index),
        'Player Breakdown': (player_breakdown, player_breakdown.dtypes[player_breakdown.dtypes != 'object'].index),
        'General Overview': (general_overview, ['Winnings', 'Winning per Person'])
    })


def get_selected_numbers(path: str = './Selected Numbers.xlsx'):
    selected = pd.read_excel(path, engine='openpyxl')

    if not selected['Name'].is_unique:
        duplicates = selected['Name'].value_counts()
        raise ValueError(f'Selected numbers needs unique Name column. Correct:{duplicates[duplicates > 1]}')

    number_cols = [col for col in selected.columns if col.startswith('Number')]
    assert_values_in_range(selected, cols=number_cols, start=1, end=50)

    star_cols = [col for col in selected.columns if col.startswith('Lucky Star')]
    assert_values_in_range(selected, cols=star_cols, start=1, end=12)

    return selected
