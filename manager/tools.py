import re
from datetime import timedelta, date
from typing import Iterable

import pandas as pd


def get_last_friday_date(run_date: date) -> (date, str):
    """ User only runs on fridays. Therefore, given any date, function determines the
        date which the last friday occurred on.
    """
    weekday_num = run_date.isoweekday()
    if weekday_num > 5:
        diff = weekday_num - 5
    elif weekday_num < 5:
        diff = 7 - (5 - weekday_num)
    else:
        diff = 0
    last_fri = run_date - timedelta(days=diff)
    return last_fri, last_fri.strftime('%Y_%m_%d_%b_%a')


def assert_values_in_range(data: pd.DataFrame, start: int, end: int, cols: list) -> None:
    """ checks if selected numbers in given data are within a range. """
    if not cols:
        cols = data.columns
    if not set(cols).issubset(data.columns):
        raise KeyError(f'{set(cols).difference(data.columns)} not in date.columns.')
    for col in cols:
        if not pd.api.types.is_numeric_dtype(data[col]):
            raise TypeError(f'data["{col}"] is not numeric.')
    mask = data[cols].isin(range(start, end + 1)).all(axis=1)
    if not mask.all():
        raise ValueError(f'The following data are not between [{start}, {end}] inclusive:\n{data[~mask]}')


def has_needed_columns(cols: Iterable[str]) -> None:
    needed = {'Name', 'Number_1', 'Number_2', 'Number_3', 'Number_4', 'Number_5', 'Lucky_Star_1', 'Lucky_Star_2'}
    if not needed.issubset(cols):
        raise ValueError(f'Key Columns: {needed.difference(cols)} are missing from selected numbers.')
    return


def validate_selected_numbers(path: str = './selected_numbers.csv') -> None:
    """ Read manager.selected_numbers ('./selected_numbers.csv') from BigQuery and validates them. Ensures:
        * dataframe to be written to BigQuery has all the correct columns.
        * there are no duplicates in Name col.
        * numbers selected are within valid ranges.

    """
    selected_numbers = pd.read_csv(path)

    has_needed_columns(selected_numbers.columns)

    if not selected_numbers['Name'].is_unique:
        duplicates = selected_numbers['Name'].value_counts()
        raise ValueError(f'"Name" in Selected numbers needs to be unique. Correct:\n{duplicates[duplicates > 1]}')

    number_cols = [col for col in selected_numbers.columns if col.startswith('Number_')]
    assert_values_in_range(selected_numbers, start=1, end=50, cols=number_cols)

    star_cols = [col for col in selected_numbers.columns if col.startswith('Lucky_Star_')]
    assert_values_in_range(selected_numbers, start=1, end=12, cols=star_cols)

    return
