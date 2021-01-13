import os

import pandas as pd
import google.cloud.bigquery as bq

from bigquery.read import get_dataset_ids_with_results
from manager.bigquery.read import read_selected_numbers
from manager.bigquery.write import create_bigquery_dataset, write_dataframe_to_bigquery, write_dictionary_to_bigquery
from manager.bigquery.queries import run_query, create_general_summary_query, create_player_summary_query


def establish_results_in_bigquery(
        dataset_name: str, results: pd.DataFrame, draw_result: dict, prize_breakdown: dict) -> None:
    """ High level function which "establishes" given results in BigQuery. This includes:
             - creating a dataset if one doesn't already exist
             - writing additional results to the dataset which was just created.
    """
    bq_client = bq.Client()

    create_bigquery_dataset(bq_client, dataset_name=dataset_name)

    write_dataframe_to_bigquery(bq_client, data=results, table_name='results', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=draw_result, col_names=['Draw', 'Outcome'],
                                 table_name='draw_outcome', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=prize_breakdown, col_names=['Match_Type', 'Prize_Per_UK_Winner'],
                                 table_name='prize_breakdown', dataset_name=dataset_name)

    print(f'Successfully written all results to BigQuery {os.getenv("PROJECT_ID")}.{dataset_name}')
    return


def cumulating_results() -> None:
    """ High level function which runs queries on all results results tables in the selected dataset_ids.
        Queries will produce bespoke summary tables from all results.
    """
    bq_client = bq.Client()

    datasets_ids_with_results = get_dataset_ids_with_results(bq_client)

    if datasets_ids_with_results:
        run_query(
            client=bq_client,
            query=create_general_summary_query(dataset_ids=datasets_ids_with_results),
            destination_table_name='general_summary'
        )
        run_query(
            client=bq_client,
            query=create_player_summary_query(dataset_ids=datasets_ids_with_results),
            destination_table_name='player_summary'
        )
    else:
        print('func "cumulating_results" Found No Datasets with results')

    return
