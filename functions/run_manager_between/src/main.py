import asyncio
import json

import aiohttp
import pandas as pd

from utilities import extract_date_field_from_request, create_authenticated_cloud_function_header


def run_manager_between(request):
    start_date = extract_date_field_from_request(request, 'start_date')
    end_date = extract_date_field_from_request(request, 'end_date')

    if start_date >= end_date:
        print(f'Start Date: {start_date} is NOT before End Date: {end_date}. Stopping here.')
        return

    date_collection = pd.date_range(start_date, end_date, freq="7D")
    pass
