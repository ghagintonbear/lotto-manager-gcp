from pytest import fixture

from manager.cumulate_results import (
    calculate_general_overview_row
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

