import os

import google.cloud.bigquery as bq
import pandas as pd
from google.cloud.exceptions import NotFound

from cloud_utils.logging import cloud_log


def write_dictionary_to_bigquery(client: bq.Client, data: dict, col_names: list, table_name: str, dataset_name: str):
    data = dict(zip(col_names, [data.keys(), data.values()]))
    data = pd.DataFrame.from_dict(data, orient='columns')

    write_dataframe_to_bigquery(client, data=data.astype(str), table_name=table_name, dataset_name=dataset_name)
    return


def write_dataframe_to_bigquery(client: bq.Client, data: pd.DataFrame, table_name: str, dataset_name: str):
    table_id = '.'.join([os.getenv('PROJECT_ID'), dataset_name, table_name])

    job_config = bq.LoadJobConfig(
        # Specify a (partial) schema. All columns are always written to the
        # table. The schema is used to assist in data type definitions.
        schema=[
            # pandas dtype "object" is ambiguous and cannot be auto-detected.
            bq.SchemaField(col, bq.enums.SqlTypeNames.STRING) for col in data.dtypes[data.dtypes == 'object'].index
        ],
        # WRITE_TRUNCATE replaces the table with the loaded data.
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(
        data,
        table_id,
        job_config=job_config
    )  # Make an API request.
    job.result()  # Wait for the job to complete.

    table = client.get_table(table_id)  # Make an API request.
    cloud_log(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
    return


def create_bigquery_dataset(client: bq.Client, dataset_name: str):
    dataset_id = os.getenv('PROJECT_ID') + '.' + dataset_name

    try:
        client.get_dataset(dataset_id)  # Make an API request.
        cloud_log(f"Dataset {dataset_id} already exists")

    except NotFound:
        cloud_log(f"Dataset {dataset_id} is not found. Attempting to create it.", 'warning')
        dataset = bq.Dataset(dataset_id)
        dataset.location = os.getenv('REGION')
        dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
        cloud_log(f"Created dataset {client.project}.{dataset.dataset_id}", 'warning')

    return
