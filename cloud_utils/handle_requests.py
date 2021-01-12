from typing import Union


def extract_field_from_request(request, field_name: str) -> Union[str, dict]:
    """ generalised function of logic shown here: https://cloud.google.com/functions/docs/writing/http#sample_usage """
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

    return field_contents
