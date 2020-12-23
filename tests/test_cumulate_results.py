from pytest import fixture

from manager.cumulate_results import (
    calculate_general_overview_row, calculate_player_prize_breakdown
)


@fixture
def result_data():
    import pandas as pd

    return pd.DataFrame({
        'Name': ['Johnson', 'Baby', 'Shampoo'],
        'Match Type': ['Match 1', 'Match 3 + 2 Stars', 'Jackpot'],
        'Prize': ["£0.00", "£6.99", "£1,000,00"]
    })


@fixture
def play_date():
    return 'Fri 99 Aug 2027'


@fixture
def play_interval():
    return 'Interval_a'


def test_calculate_general_overview_row_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = result_data['Prize'].str.replace(r'[£,]', '').astype(float)

    expected = {
        'Interval': [play_interval],
        'Play Date': [play_date],
        'Winnings': [100006.99],
        'Num of Players': [3],
        'Winning per Person': [33335.66333333334],
        'Winning Description': ['Match 3 + 2 Stars; Jackpot'],
    }

    outcome = calculate_general_overview_row(result_data, {}, play_interval, play_date)

    assert outcome == expected


def test_calculate_general_overview_row_non_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = result_data['Prize'].str.replace(r'[£,]', '').astype(float)
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
        'Winning per Person': [0.33, 33335.66333333334],
        'Winning Description': ['', 'Match 3 + 2 Stars; Jackpot'],
    }

    outcome = calculate_general_overview_row(result_data, pre_store, play_interval, play_date)

    assert outcome == expected


def test_calculate_player_prize_breakdown_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = result_data['Prize'].str.replace(r'[£,]', '').astype(float)

    expected = {
        'players': {'Johnson', 'Baby', 'Shampoo'},
        'Interval': [play_interval],
        'Play Date': [play_date],
        'Johnson': [33335.66333333334],
        'Baby': [33335.66333333334],
        'Shampoo': [33335.66333333334]
    }

    outcome = calculate_player_prize_breakdown(result_data, {}, play_interval, play_date)

    assert outcome == expected


def test_calculate_player_prize_breakdown_non_empty_store(result_data, play_interval, play_date):
    result_data['Prize'] = result_data['Prize'].str.replace(r'[£,]', '').astype(float)

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
        'Johnson': [10, 12.56, 33335.66333333334],
        'Baby': [10, 12.56, 33335.66333333334],
        'Shampoo': [None, None, 33335.66333333334],
        'Kenny': [10, 12.56, None],
        'Guido': [10, 12.56, None]
    }

    outcome = calculate_player_prize_breakdown(result_data, pre_store, play_interval, play_date)

    assert outcome == expected
