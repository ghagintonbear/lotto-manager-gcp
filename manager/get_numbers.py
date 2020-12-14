from datetime import timedelta, datetime


def get_fri_date_str(date: datetime) -> (datetime, str):
    weekday_num = date.isoweekday()
    if weekday_num > 5:
        diff = weekday_num - 5
    elif weekday_num < 5:
        diff = 7 - (5 - weekday_num)
    else:
        diff = 0
    last_fri = date - timedelta(days=diff)
    last_fri_str = f"Fri {last_fri:%d}" + f" {last_fri:%B}"[0:4] + f" {last_fri:%Y}"
    return last_fri, last_fri_str
