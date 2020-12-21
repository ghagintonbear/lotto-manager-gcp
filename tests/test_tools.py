import datetime

import pytest

from manager.tools import get_last_friday_date, get_folder_name


@pytest.mark.parametrize(
    'today, last_fri, last_fri_str',
    [
        (datetime.datetime(2020, 12, 10), datetime.datetime(2020, 12, 4), 'Fri 04 Dec 2020'),
        (datetime.datetime(2020, 12, 11), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
        (datetime.datetime(2020, 12, 12), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
        (datetime.datetime(2020, 12, 13), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
        (datetime.datetime(2020, 12, 14), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
        (datetime.datetime(2020, 12, 15), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
        (datetime.datetime(2020, 12, 16), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020')
    ]
)
def test_get_fri_date_str(today, last_fri, last_fri_str):
    assert get_last_friday_date(today) == (last_fri, last_fri_str)


@pytest.mark.parametrize(
    'date, folder_name',
    [
        (datetime.date(2020, 2, 16), '2020-02-07__2020-03-06'),
        (datetime.date(2020, 3, 23), '2020-03-06__2020-04-03'),
        (datetime.date(2020, 6, 11), '2020-05-29__2020-06-26'),
        (datetime.date(2020, 8, 21), '2020-07-24__2020-08-21'),
        (datetime.date(2020, 9, 17), '2020-08-21__2020-09-18'),
        (datetime.date(2020, 10, 4), '2020-09-18__2020-10-16'),
        (datetime.date(2021, 11, 16), '2021-11-12__2021-12-10'),
        (datetime.date(2021, 12, 5), '2021-11-12__2021-12-10'),
        (datetime.date(2022, 4, 9), '2022-04-01__2022-04-29')
    ]
)
def test_get_folder_name(date, folder_name):
    assert get_folder_name(date) == folder_name
