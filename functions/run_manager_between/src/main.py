import asyncio
import json
import os

import aiohttp
import pandas as pd

from utilities import extract_date_field_from_request, create_authenticated_cloud_function_header

""" Example JSON trigger:
{
  "start_date": "2020-08-01",
  "end_date": "2021-01-05"
}
"""

gcp_region = os.getenv('FUNCTION_REGION')
gcp_project = os.getenv('GCP_PROJECT')
publish_message_endpoint = f'https://{gcp_region}-{gcp_project}.cloudfunctions.net/publish_message'

MAXIMUM_NUMBER_OF_ATTEMPTS = 5


def run_manager_between(request):
    start_date = extract_date_field_from_request(request, 'start_date')
    end_date = extract_date_field_from_request(request, 'end_date')

    if start_date >= end_date:
        print(f'Start Date: {start_date} is NOT before End Date: {end_date}. Stopping here.')
        return

    async_results = asyncio.run(
        publish_messages_async(endpoint=publish_message_endpoint,
                               date_collection=pd.date_range(start_date, end_date, freq="7D"))
    )
    results = {}
    for result in async_results:
        results[result] = results.get(result, 0) + 1

    return json.dumps(results)


async def publish_messages_async(endpoint, date_collection):
    header = create_authenticated_cloud_function_header(endpoint)

    async with aiohttp.ClientSession(headers=header) as session:
        return await asyncio.gather(
            *(publish_message_async(session, endpoint, date) for date in date_collection),
            return_exceptions=True
        )


async def publish_message_async(session, endpoint, date):
    date_str = f'{date:%Y-%m-%d}'
    json_args = {
        "topic_name": "scheduled-weekly-9am",
        "message": f"`run_manager_between` is publishing message on `cheduled-weekly-9am` with `run_date={date_str}`",
        "run_date": date_str
    }
    for attempt_number in range(MAXIMUM_NUMBER_OF_ATTEMPTS):

        response = await session.post(endpoint, json=json_args)

        async with response:
            text_response = await response.text()

            if response.status == 200:
                print(f'Completed on attempt: #{attempt_number} for args={json_args}')
                return text_response

    print(f'Failed after {MAXIMUM_NUMBER_OF_ATTEMPTS} attempts for args={json_args}')
    return f'Failed {MAXIMUM_NUMBER_OF_ATTEMPTS} Times'
