from unittest.mock import patch
from datetime import date

from pytest import fixture, raises

from manager.scrape_results import scrape_historical_results, extract_draw_result, scrape_prize_breakdown, BASE_URL


def read_html(file_name):
    with open(f'../tests/resource/{file_name}.html') as html:
        page = html.read()
    return page


def mock_request_get(url):
    class MockResponse:
        def __init__(self, content):
            self.content = content

    if url == BASE_URL + '/results/euromillions/draw-history':
        response_content = read_html('draw_history')
    elif url == BASE_URL + '/results/euromillions/draw-history/prize-breakdown/1381':
        response_content = read_html('prize_breakdown')
    elif url == BASE_URL + '/wrong-page/results/euromillions/draw-history':
        response_content = read_html('prize_breakdown')
    elif url == BASE_URL + '/not-csv/results/euromillions/draw-history':
        response_content = read_html('draw_history_wrong_csv_link')
    else:
        response_content = 'wrong-link'

    return MockResponse(response_content)


def mock_read_csv(url):
    if url == BASE_URL + '/results/euromillions/draw-history/csv':
        return 'success'
    else:
        return 'failed'


@patch('requests.get', mock_request_get)
def test_scrape_historical_results_raise_attribute_error():

    with raises(AttributeError, match="'NoneType' object has no attribute 'get'"):
        scrape_historical_results('/wrong-page/results/euromillions/draw-history')


@patch('requests.get', mock_request_get)
def test_scrape_historical_results_raise_value_error():

    with raises(ValueError, match="Can't find csv at this link:.*"):
        scrape_historical_results('/not-csv/results/euromillions/draw-history')


@patch('pandas.read_csv', mock_read_csv)
@patch('requests.get', mock_request_get)
def test_scrape_historical_results():

    historical_results = scrape_historical_results()

    assert historical_results == 'success'


@patch('requests.get', mock_request_get)
def test_scrape_prize_breakdown():
    breakdown = scrape_prize_breakdown(draw_number=1381)

    expected_breakdown = {
        'Match 5 + 2 Stars': "£0.00",
        'Match 5 + 1 Star': "£51,956.30",
        'Match 5': "£7,727.40"
    }

    assert breakdown == expected_breakdown


@fixture
def hist_data():
    import pandas as pd

    return pd.DataFrame({
        'DrawDate': ['15-Dec-2020', '11-Dec-2020', '11-Dec-2020'],
        'Ball 1': [1, 2, 2],
        'Ball 2': [3, 4, 4],
        'Lucky Star 1': [5, 6, 6],
        'UK Millionaire Maker': ['alpha', 'beta', 'dupe-date'],
        'DrawNumber': [1966, 2012, 2012]
    })


def test_extract_draw_result_incorrect_date(hist_data):
    draw_date = date(2020, 1, 15)
    with raises(Exception, match=r'Selected draw_date: .* not in hist_results\[\"DrawDate\"\]'):
        extract_draw_result(draw_date, hist_data)


def test_extract_draw_result_matches_multiple_dates(hist_data):
    draw_date = date(2020, 12, 11)
    with raises(Exception, match=r'Selected draw_date: .* maps to many in hist_results\[\"DrawDate\"\]'):
        extract_draw_result(draw_date, hist_data)


def test_extract_draw_result_valid_date(hist_data):
    draw_date = date(2020, 12, 15)

    expected_result = {
        'DrawDate': '2020-12-15-Tue', 'Ball 1': 1, 'Ball 2': 3, 'Lucky Star 1': 5,
        'UK Millionaire Maker': 'alpha', 'DrawNumber': 1966
    }

    draw_result = extract_draw_result(draw_date, hist_data)

    assert draw_result == expected_result
