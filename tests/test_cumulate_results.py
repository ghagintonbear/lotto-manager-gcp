from unittest.mock import patch, MagicMock

from pytest import fixture
from pandas.testing import assert_frame_equal

from manager.tools import currency_to_int
from manager.cumulate_results import (
    calculate_general_overview_row, calculate_player_prize_breakdown, compute_cumulated_result
)


@fixture
def result_data():
    import pandas as pd

    return pd.DataFrame({
        'Name': ['Johnson', 'Baby', 'Shampoo'],
        'Match Type': ['Match 1', 'Match 3 + 2 Stars', 'Jackpot'],
        'Prize': ["£0.00", "£6.99", "£1,000,00.00"]
    })


@fixture
def play_date():
    return 'Fri 99 Aug 2027'


@fixture
def play_interval():
    return 'Interval_a'


def test_calculate_general_overview_row_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = currency_to_int(result_data['Prize'])

    expected = {
        'Interval': [play_interval],
        'Play Date': [play_date],
        'Winnings': [100006.99],
        'Num of Players': [3],
        'Winning per Person': [10000699 / (3 * 100)],
        'Winning Description': ['Match 3 + 2 Stars; Jackpot'],
    }

    outcome = calculate_general_overview_row(result_data, {}, play_interval, play_date)

    assert outcome == expected


def test_calculate_general_overview_row_non_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = currency_to_int(result_data['Prize'])
    pre_store = {
        'Interval': ['Interval_b'],
        'Play Date': ['Fri 99 Aug 2027'],
        'Winnings': [0.99],
        'Num of Players': [10],
        'Winning per Person': [0.33],
        'Winning Description': [''],
    }

    expected = {
        'Interval': ['Interval_b', play_interval],
        'Play Date': ['Fri 99 Aug 2027', play_date],
        'Winnings': [0.99, 100006.99],
        'Num of Players': [10, 3],
        'Winning per Person': [0.33, 10000699 / (3 * 100)],
        'Winning Description': ['', 'Match 3 + 2 Stars; Jackpot'],
    }

    outcome = calculate_general_overview_row(result_data, pre_store, play_interval, play_date)

    assert outcome == expected


def test_calculate_player_prize_breakdown_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = currency_to_int(result_data['Prize'])

    expected = {
        'players': {'Johnson', 'Baby', 'Shampoo'},
        'Interval': [play_interval],
        'Play Date': [play_date],
        'Johnson': [10000699 / (3 * 100)],
        'Baby': [10000699 / (3 * 100)],
        'Shampoo': [10000699 / (3 * 100)]
    }

    outcome = calculate_player_prize_breakdown(result_data, {}, play_interval, play_date)

    assert outcome == expected


def test_calculate_player_prize_breakdown_non_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = currency_to_int(result_data['Prize'])

    pre_store = {
        'players': {'Johnson', 'Baby', 'Kenny', 'Guido'},
        'Interval': ['Interval_b', 'Interval_c'],
        'Play Date': ['play_date_1', 'play_date_2'],
        'Johnson': [10, 12.56],
        'Baby': [10, 12.56],
        'Kenny': [10, 12.56],
        'Guido': [10, 12.56]
    }

    expected = {
        'players': {'Johnson', 'Baby', 'Shampoo', 'Kenny', 'Guido'},
        'Interval': ['Interval_b', 'Interval_c', play_interval],
        'Play Date': ['play_date_1', 'play_date_2', play_date],
        'Johnson': [10, 12.56, 10000699 / (3 * 100)],
        'Baby': [10, 12.56, 10000699 / (3 * 100)],
        'Shampoo': [None, None, 10000699 / (3 * 100)],
        'Kenny': [10, 12.56, None],
        'Guido': [10, 12.56, None]
    }

    outcome = calculate_player_prize_breakdown(result_data, pre_store, play_interval, play_date)

    assert outcome == expected


def mock_glob(path):
    return ['.\\test\\int_a\\date_1.xlsx', '.\\test\\int_b\\date_2.xlsx', '.\\test\\int_c\\date_3.xlsx']


@patch('glob.glob', mock_glob)
def test_compute_cumulated_result(result_data):
    from pandas import DataFrame

    result_data_2 = DataFrame({
        'Name': ['Nivea', 'Cat', 'Shampoo'],
        'Match Type': ['Match 3', 'Match 2', 'Match 9'],
        'Prize': ["£1.00", "£2.00", "£0.00"]
    })
    result_data_3 = DataFrame({
        'Name': ['Nivea', 'Baby', 'Shampoo'],
        'Match Type': ['', '', ''],
        'Prize': ["£0.00", "£0.00", "£0.00"]
    })

    expected_overview = DataFrame({
        'Interval': ['int_a', 'int_b', 'int_c'],
        'Play Date': ['date_1', 'date_2', 'date_3'],
        'Winnings': [100006.99, 3.0, 0],
        'Num of Players': [3, 3, 3],
        'Winning per Person': [10000699 / (3 * 100), 1.0, 0],
        'Winning Description': ['Match 3 + 2 Stars; Jackpot', 'Match 3; Match 2', ''],
    })

    expected_breakdown = DataFrame({
        'Interval': ['int_a', 'int_b', 'int_c'],
        'Play Date': ['date_1', 'date_2', 'date_3'],
        'Shampoo': [33335.66333333334, 1.0, 0],
        'Baby': [33335.66333333334, None, 0],
        'Johnson': [33335.66333333334, None, None],
        'Cat': [None, 1.0, None],
        'Nivea': [None, 1.0, 0]
    })

    with patch('pandas.read_excel', MagicMock(side_effect=[result_data, result_data_2, result_data_3])):
        overview, breakdown = compute_cumulated_result()
        assert_frame_equal(overview[overview.columns.sort_values()],
                           expected_overview[expected_overview.columns.sort_values()])
        assert_frame_equal(breakdown[breakdown.columns.sort_values()],
                           expected_breakdown[expected_breakdown.columns.sort_values()])
