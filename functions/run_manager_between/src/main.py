import asyncio
import json
import os
from random import uniform

import aiohttp
import pandas as pd

from utilities import extract_date_field_from_request, create_authenticated_cloud_function_header

""" Example JSON trigger:
{
  "start_date": "2020-08-01",
  "end_date": "2021-01-05"
}
"""

gcp_region = os.getenv('REGION')
gcp_project = os.getenv('PROJECT_ID')
publish_message_endpoint = f'https://{gcp_region}-{gcp_project}.cloudfunctions.net/publish_message'

MAXIMUM_NUMBER_OF_ATTEMPTS = 5


def run_manager_between(request):
    start_date = extract_date_field_from_request(request, 'start_date')
    end_date = extract_date_field_from_request(request, 'end_date')

    if start_date >= end_date:
        print(f'Start Date: {start_date} is NOT before End Date: {end_date}. Stopping here.')
        return

    date_collection = pd.date_range(start_date, end_date, freq="7D")
    date_cumulate_flag_collection = list(zip(date_collection, (date_collection == date_collection.max()).astype(str)))

    async_results = asyncio.run(
        publish_messages_async(endpoint=publish_message_endpoint,
                               collection=date_cumulate_flag_collection)
    )
    results = {}
    for result in async_results:
        results[str(result)] = results.get(result, 0) + 1

    return json.dumps(results)


async def publish_messages_async(endpoint, collection):
    header = create_authenticated_cloud_function_header(endpoint)

    async with aiohttp.ClientSession(headers=header) as session:
        return await asyncio.gather(
            *(publish_message_async(session, endpoint, date, cumulate_flag) for date, cumulate_flag in collection),
            return_exceptions=True
        )


async def publish_message_async(session, endpoint, date, cumulate_flag):
    date_str = f'{date:%Y-%m-%d}'
    json_args = {
        "topic_name": "scheduled-weekly-9am",
        "message": f"`run_manager_between` asked to publish on `scheduled-weekly-9am` for `run_date={date_str}`",
        "attributes": {
            "run_date": date_str,
            "cumulate_results": cumulate_flag
        }
    }
    failed_attempts = []
    for attempt_number in range(MAXIMUM_NUMBER_OF_ATTEMPTS):

        response = await session.post(endpoint, json=json_args)

        async with response:
            text_response = await response.text()

            if response.status == 200:
                print(f'Completed on attempt: #{attempt_number} for args={json_args}')
                return text_response
            else:
                failed_attempts.append((response.status, endpoint, text_response))
                # No need to wait after the last attempt, we've given up now - so don't waste compute cycles
                if attempt_number < MAXIMUM_NUMBER_OF_ATTEMPTS - 1:
                    sleep_time = uniform(1, 16)
                    await asyncio.sleep(sleep_time)
                    print(f'run_manager_between slept for: {sleep_time:.2f}s')

    print(f'Failed after {MAXIMUM_NUMBER_OF_ATTEMPTS} attempts for args={json_args}. Reasons: {failed_attempts}')
    return f'Failed {MAXIMUM_NUMBER_OF_ATTEMPTS} Times'
