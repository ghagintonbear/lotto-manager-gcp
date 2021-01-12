import requests


def create_authenticated_cloud_function_header(cloud_function_endpoint: str) -> dict:
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
