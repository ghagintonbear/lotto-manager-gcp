import os
from datetime import timedelta, datetime

import pandas as pd


def get_last_friday_date(date: datetime) -> (datetime, str):
    """ User only runs on fridays. Therefore, given any date, function determines the
        date which the last friday occurred on.
    """
    weekday_num = date.isoweekday()
    if weekday_num > 5:
        diff = weekday_num - 5
    elif weekday_num < 5:
        diff = 7 - (5 - weekday_num)
    else:
        diff = 0
    last_fri = (date - timedelta(days=diff)).date()
    last_fri_str = f"Fri {last_fri:%d}" + f" {last_fri:%B}"[0:4] + f" {last_fri:%Y}"
    return last_fri, last_fri_str


def get_folder_name(selected_date: datetime) -> str:
    """
    organise generated results into date range folders within ../results_archive.
    `date_range_start(end)` provided by user.
    if selected_date > end_range then it goes in the folder that starts there.
    """
    def date_to_str(date: datetime) -> str: return f"{date:%Y-%m-%d}"

    date_range_start = datetime(2020, 1, 10)
    date_range_end = datetime(2030, 12, 31)
    date_range_df = pd.DataFrame({
        'start': pd.date_range(date_range_start, date_range_end, freq='28D'),
        'end': pd.date_range(date_range_start + timedelta(days=28), date_range_end + timedelta(days=28), freq='28D')
    })
    for col in date_range_df.columns:
        assert all(date_range_df[col].dt.day_name() == 'Friday'), f'date_range_df: {col} dates do not land on a friday'

    selected_date = pd.to_datetime(selected_date)
    folder_start_date, folder_end_date = date_range_df[date_range_df['end'] >= selected_date].iloc[0, :]
    folder_name = date_to_str(folder_start_date) + '__' + date_to_str(folder_end_date)

    return folder_name


def make_results_folder(folder_name: str) -> str:
    """
    makes sure appropriate directories exist to store generated results.
    """
    results_folder = 'result_archive'

    if results_folder not in os.listdir():
        os.mkdir(f'./{results_folder}')

    path_to_new_folder = f'./{results_folder}/{folder_name}'
    if folder_name not in os.listdir(f'./{results_folder}/'):
        os.mkdir(path_to_new_folder)

    return path_to_new_folder


def add_sum_row(col: str, data: pd.DataFrame) -> pd.DataFrame:
    total = data.sum()
    total[col] = 'SUM'
    return data.append(total, ignore_index=True)
