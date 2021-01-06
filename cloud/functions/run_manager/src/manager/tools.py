from datetime import timedelta, date

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
    last_fri_str = f"Fri {last_fri:%d}" + f" {last_fri:%B}"[0:4] + f" {last_fri:%Y}"
    return last_fri, last_fri_str


def add_sum_row(col: str, data: pd.DataFrame) -> pd.DataFrame:
    total = data.sum()
    total[col] = 'SUM'
    return data.append(total, ignore_index=True)


def assert_values_in_range(data: pd.DataFrame, start: int, end: int, cols: list):
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


def currency_to_int(currency: pd.Series) -> pd.Series:
    """ removes all non digit characters. Moved to func to test."""
    return currency.str.replace(r'[\D]', '').astype('int64')
