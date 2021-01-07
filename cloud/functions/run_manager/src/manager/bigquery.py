import os

import pandas as pd
import google.cloud.bigquery as bq

from manager.tools import assert_values_in_range


def read_selected_numbers():
    """ Read selected.numbers ('./selected_numbers.csv') from BigQuery and validates them.
        Ensures numbers selected are valid and there are no duplicates in Name col.
    """
    select_all_query = f"""
    SELECT *
    FROM `{os.getenv('PROJECT_ID')}.selected.numbers`"""
    selected_numbers = pd.read_gbq(select_all_query)

    if not selected_numbers['Name'].is_unique:
        duplicates = selected_numbers['Name'].value_counts()
        raise ValueError(f'"Name" in Selected numbers needs to be unique. Correct:\n{duplicates[duplicates > 1]}')

    number_cols = [col for col in selected_numbers.columns if col.startswith('Number_')]
    assert_values_in_range(selected_numbers, start=1, end=50, cols=number_cols)

    star_cols = [col for col in selected_numbers.columns if col.startswith('Lucky_Star_')]
    assert_values_in_range(selected_numbers, start=1, end=12, cols=star_cols)

    return selected_numbers


def write_dictionary_to_bigquery(client: bq.Client, data: dict, col_names: list, table_name: str, dataset_name: str):
    table_id = '.'.join([os.getenv('PROJECT_ID'), dataset_name, table_name])

    data_list = [dict(zip(col_names, values)) for values in data.items()]

    job_config = bq.LoadJobConfig(
        schema=[bq.SchemaField(col, bq.enums.SqlTypeNames.STRING) for col in col_names],
        # WRITE_TRUNCATE replaces the table with the loaded data.
        write_disposition="WRITE_TRUNCATE",
    )

    load_job = client.load_table_from_json(
        data_list,
        table_id,
        location=os.getenv('REGION'),  # Must match the destination dataset location.
        job_config=job_config,
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    destination_table = client.get_table(table_id)
    print("Loaded {} rows.".format(destination_table.num_rows))
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
    print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")
    return


# def create_bigquery_table(client: bq.Client, dataset_name: str, table_name: str, schema: dict):
#     schema_list = []
#     for col_name, field_type in schema.items():
#         column = bq.SchemaField(col_name, field_type, mode="REQUIRED")
#         schema_list.append(column)
#
#     table_id = ".".join([os.getenv('PROJECT_ID'), dataset_name, table_name])
#     table = bq.Table(table_id, schema=schema_list)
#     table = client.create_table(table)
#
#     print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
#     return


def create_bigquery_dataset(client: bq.Client, dataset_name: str):
    dataset = bq.Dataset(os.getenv('PROJECT_ID') + '.' + dataset_name)
    dataset.location = os.getenv('REGION')

    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    print(f"Created dataset {client.project}.{dataset.dataset_id}")
    return


def establish_results_in_bigquery(dataset_name: str, results: pd.DataFrame, draw_result: dict, prize_breakdown: dict):
    bq_client = bq.Client()

    create_bigquery_dataset(bq_client, dataset_name=dataset_name)

    write_dataframe_to_bigquery(bq_client, data=results, table_name='results', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=draw_result, col_names=['Draw', 'Outcome'],
                                 table_name='draw_outcome', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=prize_breakdown, col_names=['Match Type', 'Prize Per UK Winner'],
                                 table_name='prize_breakdown', dataset_name=dataset_name)

    print(f'Successfully written all results to BigQuery {os.getenv("PROJECT_ID")}.{dataset_name}')
    return
