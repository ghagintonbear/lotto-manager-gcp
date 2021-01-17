import os

import google.cloud.bigquery as bq
import pandas as pd
from google.cloud.exceptions import NotFound


def write_dictionary_to_bigquery(
        client: bq.Client, data: dict, col_names: [str, str], table_name: str, dataset_name: str) -> None:
    """ First converts dict to DataFrame, structure: {col_name: data.keys(), col_name: data.values()}
        Then passes the result to write_dataframe_to_bigquery. """
    data = dict(zip(col_names, [data.keys(), data.values()]))
    data = pd.DataFrame.from_dict(data, orient='columns')

    write_dataframe_to_bigquery(client, data=data.astype(str), table_name=table_name, dataset_name=dataset_name)
    return


def write_dataframe_to_bigquery(client: bq.Client, data: pd.DataFrame, table_name: str, dataset_name: str) -> str:
    """ Writes Pandas Dataframe to given BigQuery dataset_name. Always overwrites existing data if any. """
    table_id = '.'.join([client.project, dataset_name, table_name])

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
    result = f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}"
    print(result)
    return result


def create_bigquery_dataset(client: bq.Client, dataset_name: str) -> str:
    """ Creates BigQuery dataset, if one doesn't exist already. """
    dataset_id = client.project + '.' + dataset_name

    try:
        client.get_dataset(dataset_id)  # Make an API request.
        result = f"Dataset {dataset_id} already exists"

    except NotFound:
        print(f"Dataset {dataset_id} is not found. Attempting to create it.")
        dataset = bq.Dataset(dataset_id)
        dataset.location = os.getenv('REGION')
        dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
        result = f"Created dataset {client.project}.{dataset.dataset_id}"

    print(result)
    return result
