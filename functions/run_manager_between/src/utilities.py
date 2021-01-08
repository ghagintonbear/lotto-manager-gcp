from datetime import date, datetime

import requests


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


def create_authenticated_cloud_function_header(cloud_function_endpoint: str):
    """ For function to function calls - when receiving function is NOT public. See:
    https://cloud.google.com/functions/docs/securing/authenticating#function-to-function
    """
    # Set up metadata server request
    metadata_server_url = 'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience='
    token_full_url = metadata_server_url + cloud_function_endpoint
    token_headers = {'Metadata-Flavor': 'Google'}

    # Fetch the token
    token_response = requests.get(token_full_url, headers=token_headers)
    jwt = token_response.content.decode("utf-8")

    # Provide the token in the request to the receiving function
    receiving_function_headers = {'Authorization': f'bearer {jwt}'}

    return receiving_function_headers
