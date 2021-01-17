import os
import re

import pandas as pd
from google.cloud import bigquery as bq


def read_selected_numbers() -> pd.DataFrame:
    """ Read manager.selected_numbers ('./selected_numbers.csv') from BigQuery and validates them.
        Ensures numbers selected are valid and there are no duplicates in Name col.
    """
    select_all_query = f"""
    SELECT *
    FROM `{os.getenv('PROJECT_ID')}.manager.selected_numbers`"""

    return pd.read_gbq(select_all_query)


def get_dataset_ids_with_results(client: bq.Client, pattern: str = r'\d{4}_\d{2}_\d{2}_\w*') -> [str]:
    """ gathers all dataset_ids, where the the following criteria is met:
            - dataset_id is of the format of given pattern, which defaults to: YYYY_MM_DD_<additional_text>
            - dataset_id has a table called "results"
    """
    datasets_ids_with_results = []
    for dataset_list_item in client.list_datasets():
        dataset_id = dataset_list_item.dataset_id
        if re.fullmatch(pattern, dataset_id):
            tables_list = [table.table_id for table in client.list_tables(dataset=dataset_id)]
            if 'results' in tables_list:
                datasets_ids_with_results.append(dataset_id)

    return datasets_ids_with_results
