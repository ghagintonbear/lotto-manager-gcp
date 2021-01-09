import os
import re

import pandas as pd
import google.cloud.bigquery as bq

from manager.bigquery.read import read_selected_numbers
from manager.bigquery.write import create_bigquery_dataset, write_dataframe_to_bigquery, write_dictionary_to_bigquery


def establish_results_in_bigquery(dataset_name: str, results: pd.DataFrame, draw_result: dict, prize_breakdown: dict):
    bq_client = bq.Client()

    create_bigquery_dataset(bq_client, dataset_name=dataset_name)

    write_dataframe_to_bigquery(bq_client, data=results, table_name='results', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=draw_result, col_names=['Draw', 'Outcome'],
                                 table_name='draw_outcome', dataset_name=dataset_name)

    write_dictionary_to_bigquery(bq_client, data=prize_breakdown, col_names=['Match_Type', 'Prize_Per_UK_Winner'],
                                 table_name='prize_breakdown', dataset_name=dataset_name)

    print(f'Successfully written all results to BigQuery {os.getenv("PROJECT_ID")}.{dataset_name}')
    return


def cumulate_results():
    bq_client = bq.Client()

    datasets_with_results = []
    for dataset_list_item in bq_client.list_datasets():  # Make an API request.
        dataset_id = dataset_list_item.dataset_id
        if re.fullmatch(r'\d{4}_\d{2}_\d{2}_\w*_Fri', dataset_id):
            if 'results' in list(bq_client.list_tables(dataset=dataset_id)):
                datasets_with_results.append(dataset_id)

    for dataset_id in datasets_with_results:
        # compound queries which will:
        #   add a column to each table (not perm) with run_date
        #   append all the results
        #   filter out prize != $0.00
        #   convert prize to NUMERIC type
        #   groupby run_date
        #       sum prize
        #       collect match types
        #       count number of players
        #       calculate winnings per person
        # Do similar of player_breakdown table
        pass

    # write out result to manager
    return
