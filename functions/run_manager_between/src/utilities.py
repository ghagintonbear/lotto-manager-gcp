from datetime import date, datetime


def extract_date_field_from_request(request, field_name: str) -> date:
    request_json = request.get_json()
    request_args = request.args

    if request_json and field_name in request_json:
        field_contents = request_json[field_name]
    elif request_args and field_name in request_args:
        field_contents = request_args[field_name]
    else:
        message = f'"{field_name}" not defined via JSON or arguments in http header'
        print(f'ERROR: {message}')
        raise RuntimeError(message)

    return _str_to_date(field_contents)


def _str_to_date(a_date: str, date_format: str = '%Y-%m-%d') -> date:
    try:
        result_date = datetime.strptime(a_date, date_format).date()
    except ValueError as ve:
        raise ValueError(f'Date given: {a_date}, does not match expected date format: {date_format}') from ve

    return result_date
