from datetime import date
from unittest import mock

import pytest

from manager.tools import (
    get_last_friday_date, assert_values_in_range, currency_to_int
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


def test_currency_to_int():
    from pandas import Series
    from pandas.testing import assert_series_equal

    currency = Series(["£0.00", "£6.99", "£1,000,00.00", "'Â£9,9..9 9", "£%^$\"£535.34£$£%£$"])

    expected = Series([0, 699, 10000000, 9999, 53534], dtype='int64')

    assert_series_equal(currency_to_int(currency), expected)