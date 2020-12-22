from datetime import date
from unittest import mock

import pytest

from manager.tools import (
    get_last_friday_date, get_folder_name, get_selected_numbers, assert_values_in_range
)


@pytest.mark.parametrize(
    'today, last_fri, last_fri_str',
    [
        (date(2020, 12, 10), date(2020, 12, 4), 'Fri 04 Dec 2020'),
        (date(2020, 12, 11), date(2020, 12, 11), 'Fri 11 Dec 2020'),
        (date(2020, 12, 12), date(2020, 12, 11), 'Fri 11 Dec 2020'),
        (date(2020, 12, 13), date(2020, 12, 11), 'Fri 11 Dec 2020'),
        (date(2020, 12, 14), date(2020, 12, 11), 'Fri 11 Dec 2020'),
        (date(2020, 12, 15), date(2020, 12, 11), 'Fri 11 Dec 2020'),
        (date(2020, 12, 16), date(2020, 12, 11), 'Fri 11 Dec 2020')
    ]
)
def test_get_fri_date_str(today, last_fri, last_fri_str):
    assert get_last_friday_date(today) == (last_fri, last_fri_str)


@pytest.mark.parametrize(
    'a_date, folder_name',
    [
        (date(2020, 2, 16), '2020-02-07__2020-03-06'),
        (date(2020, 3, 23), '2020-03-06__2020-04-03'),
        (date(2020, 6, 11), '2020-05-29__2020-06-26'),
        (date(2020, 8, 21), '2020-07-24__2020-08-21'),
        (date(2020, 9, 17), '2020-08-21__2020-09-18'),
        (date(2020, 10, 4), '2020-09-18__2020-10-16'),
        (date(2021, 11, 16), '2021-11-12__2021-12-10'),
        (date(2021, 12, 5), '2021-11-12__2021-12-10'),
        (date(2022, 4, 9), '2022-04-01__2022-04-29')
    ]
)
def test_get_folder_name(a_date, folder_name):
    assert get_folder_name(a_date) == folder_name


@pytest.fixture
def selected_dataframe():
    import pandas as pd

    return pd.DataFrame({
        'Name': ['Snickers', 'KitKat', 'Snickers'],
        'Number 1': [1, 2, 2],
        'Number 2': [3, 4, 4],
        'Lucky Star 1': [5, 6, 6],
    })


@pytest.fixture
def selected_cols():
    return ['Number 1', 'Number 2', 'Lucky Star 1']


def test_assert_values_in_range_valid_inputs(selected_dataframe, selected_cols):

    assert assert_values_in_range(selected_dataframe, start=1, end=9, cols=selected_cols) is None


def test_assert_values_in_range_valid_inputs_empty_cols(selected_dataframe, selected_cols):

    assert assert_values_in_range(selected_dataframe[selected_cols], start=1, end=9, cols=[]) is None


def test_assert_values_in_range_raise_value_error(selected_dataframe, selected_cols):

    with pytest.raises(ValueError, match=r'The following data are not between \[2, 9] .*'):
        assert_values_in_range(selected_dataframe, start=2, end=9, cols=selected_cols)


def test_assert_values_in_range_raise_type_error(selected_dataframe, selected_cols):

    with pytest.raises(TypeError, match=r'.* is not numeric.'):
        assert_values_in_range(selected_dataframe.astype(str), start=1, end=9, cols=selected_cols)


def test_assert_values_in_range_raise_key_error(selected_dataframe):
    cols = ['Number 1', 'Number 5']
    with pytest.raises(KeyError, match=r'.* not in date.columns.'):
        assert_values_in_range(selected_dataframe.astype(str), start=1, end=9, cols=cols)


def test_get_selected_numbers_raise_value_error(selected_dataframe):
    with mock.patch('pandas.read_excel', mock.MagicMock(return_value=selected_dataframe)):
        with pytest.raises(ValueError, match=r'"Name" in Selected numbers needs to be unique\. .*'):
            get_selected_numbers()


def test_get_selected_numbers_valid_run(selected_dataframe):
    selected_dataframe.iloc[0, 0] = 'Bounty'
    with mock.patch('pandas.read_excel', mock.MagicMock(return_value=selected_dataframe)):
        assert get_selected_numbers().equals(selected_dataframe)
