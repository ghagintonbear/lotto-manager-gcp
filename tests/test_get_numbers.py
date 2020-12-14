import datetime

import pytest

from manager.get_numbers import get_fri_date_str


@pytest.mark.parametrize('today, last_fri, last_fri_str',
                         [
                             (datetime.datetime(2020, 12, 10), datetime.datetime(2020, 12, 4), 'Fri 04 Dec 2020'),
                             (datetime.datetime(2020, 12, 11), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
                             (datetime.datetime(2020, 12, 12), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
                             (datetime.datetime(2020, 12, 13), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
                             (datetime.datetime(2020, 12, 14), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
                             (datetime.datetime(2020, 12, 15), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020'),
                             (datetime.datetime(2020, 12, 16), datetime.datetime(2020, 12, 11), 'Fri 11 Dec 2020')
                         ])
def test_get_fri_date_str(today, last_fri, last_fri_str):
    assert get_fri_date_str(today) == (last_fri, last_fri_str)
