import pytest
import pandas as pd

from cloud.functions.run_manager.src.manager import collect_winning_numbers, match_type_label, check_matches_on_selected


def test_collect_numbers():
    input_results = {'DrawDate': '2020-12-15 00:00:00', 'Ball 1': 9, 'Ball 2': 13, 'Ball 3': 21, 'Ball 4': 29,
                     'Ball 5': 35, 'Lucky Star 1': 1, 'Lucky Star 2': 2, 'DrawNumber': 1381, 'ball 1': -0, 'lucky': -0}
    expected_dict = {
        'Balls': [9, 13, 21, 29, 35],
        'Lucky Stars': [1, 2]
    }
    winning_numbers = collect_winning_numbers(input_results)

    assert winning_numbers == expected_dict


@pytest.mark.parametrize('input_row, expected_label', [
    (pd.Series({'Balls Matched': 0, 'Stars Matched': 0}), 'Match 0'),
    (pd.Series({'Balls Matched': 9, 'Stars Matched': 1}), 'Match 9 + 1 Star'),
    (pd.Series({'Balls Matched': 2, 'Stars Matched': 2}), 'Match 2 + 2 Stars'),
    (pd.Series({'Balls Matched': 2, 'Stars Matched': 3}), None),
    (pd.Series({'Balls Matched': -1, 'Stars Matched': 1}), None),
    (pd.Series({'Balls Matched': -9, 'Stars Matched': 2}), None),
])
def test_match_type_label(input_row, expected_label):
    assert match_type_label(input_row) == expected_label


def test_check_matches_on_selected():
    selected = pd.DataFrame({
        'Name': ['Peter', 'Crouch', 'Special', 'One'],
        'Number 1': [1, 6, 7, 99], 'Number 2': [7, 5, 9, 1], 'Number 3': [9, 10, 1, 99],
        'Lucky Star 1': [1, 2, 99, 3], 'Lucky Star 2': [3, 4, 99, 1]
    })
    winning = {
        'Balls': [1, 7, 9],
        'Lucky Stars': [1, 3]
    }
    prize_breakdown = {
        'Match 3 + 2 Stars': '£40.10', 'Match 2 + 2 Stars': '£9.90', 'Match 3 + 1 Star': '£6.00',
        'Match 3': '£4.80', 'Match 1 + 2 Stars': '£4.90', 'Match 2 + 1 Star': '£3.20', 'Match 2': '£2.20'
    }
    expected_result = pd.DataFrame({
        'Name': ['Peter', 'Crouch', 'Special', 'One'],
        'Number 1': [1, 6, 7, 99], 'Number 2': [7, 5, 9, 1], 'Number 3': [9, 10, 1, 99],
        'Lucky Star 1': [1, 2, 99, 3], 'Lucky Star 2': [3, 4, 99, 1],
        # expected to be added on
        'Balls Matched': [3, 0, 3, 1], 'Stars Matched': [2, 0, 0, 2],
        'Match Type': ['Match 3 + 2 Stars', 'Match 0', 'Match 3', 'Match 1 + 2 Stars'],
        'Prize': ['£40.10', '£0.00', '£4.80', '£4.90']
    })
    pd.testing.assert_frame_equal(
        left=check_matches_on_selected(selected, winning, prize_breakdown),
        right=expected_result
    )
