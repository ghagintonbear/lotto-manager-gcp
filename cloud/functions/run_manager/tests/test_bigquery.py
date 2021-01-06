from unittest import mock

import pytest

from manager.bigquery import get_selected_numbers


@pytest.fixture
def selected_dataframe():
    import pandas as pd

    return pd.DataFrame({
        'Name': ['Snickers', 'KitKat', 'Snickers'],
        'Number_1': [1, 2, 2],
        'Number_2': [3, 4, 4],
        'Lucky_Star_1': [5, 6, 6],
    })


def test_get_selected_numbers_raise_value_error(selected_dataframe):
    with mock.patch('pandas.read_gbq', mock.MagicMock(return_value=selected_dataframe)):
        with pytest.raises(ValueError, match=r'"Name" in Selected numbers needs to be unique\. .*'):
            get_selected_numbers()


def test_get_selected_numbers_valid_run(selected_dataframe):
    selected_dataframe.iloc[0, 0] = 'Bounty'
    with mock.patch('pandas.read_gbq', mock.MagicMock(return_value=selected_dataframe)):
        assert get_selected_numbers().equals(selected_dataframe)
