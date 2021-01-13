from datetime import date
from unittest import mock

import pytest

from manager.tools import (
    get_last_friday_date, assert_values_in_range, validate_selected_numbers, _make_names_bq_safe, _has_needed_columns
)


@pytest.mark.parametrize(
    'today, last_fri, last_fri_str',
    [
        (date(2020, 12, 10), date(2020, 12, 4), '2020_12_04_Dec_Fri'),
        (date(2020, 12, 11), date(2020, 12, 11), '2020_12_11_Dec_Fri'),
        (date(2020, 12, 12), date(2020, 12, 11), '2020_12_11_Dec_Fri'),
        (date(2020, 12, 13), date(2020, 12, 11), '2020_12_11_Dec_Fri'),
        (date(2020, 12, 14), date(2020, 12, 11), '2020_12_11_Dec_Fri'),
        (date(2020, 12, 15), date(2020, 12, 11), '2020_12_11_Dec_Fri'),
        (date(2020, 12, 16), date(2020, 12, 11), '2020_12_11_Dec_Fri')
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
    return ['Number_1', 'Number_2', 'Lucky_Star_1']


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
    cols = ['Number_6', 'Number_7']
    with pytest.raises(KeyError, match=r'.* not in date.columns.'):
        assert_values_in_range(selected_dataframe.astype(str), start=1, end=9, cols=cols)


@pytest.fixture
def selected_dataframe():
    import pandas as pd

    return pd.DataFrame({
        'Name': ['Snickers', 'KitKat', 'Snickers'],
        'Number_1': [1, 2, 2],
        'Number_2': [3, 4, 4],
        'Number_3': [3, 4, 4],
        'Number_4': [3, 4, 4],
        'Number_5': [3, 4, 4],
        'Lucky_Star_1': [5, 6, 6],
        'Lucky_Star_2': [5, 6, 6]
    })


def test_get_selected_numbers_raise_value_error(selected_dataframe):
    with mock.patch('pandas.read_csv', mock.MagicMock(return_value=selected_dataframe)):
        with pytest.raises(ValueError, match=r'"Name" in Selected numbers needs to be unique\. .*'):
            validate_selected_numbers()


def test_get_selected_numbers_valid_run(selected_dataframe):
    selected_dataframe.iloc[0, 0] = 'Bounty'
    with mock.patch('pandas.read_csv', mock.MagicMock(return_value=selected_dataframe)):
        assert validate_selected_numbers() is None


def test_has_needed_columns_raises_value_error(selected_cols):
    with pytest.raises(ValueError, match=r'Key Columns: .* are missing from selected numbers.'):
        _has_needed_columns(selected_cols)


def test_has_needed_columns(selected_dataframe):
    assert _has_needed_columns(selected_dataframe.columns) is None


def test_make_names_bq_safe_raises_value_error():
    with pytest.raises(ValueError, match='Invalid Name: .*'):
        _make_names_bq_safe('!@#$%^&*')


def test_make_names_bq_safe_return_valid_input():
    name = 'Valid_Name42'
    assert _make_names_bq_safe(name) == name


def test_make_names_bq_safe_return_valid_chars():
    name = ' !&#* V@lid_Name42 /*'
    assert _make_names_bq_safe(name) == 'V_lid_Name42'
