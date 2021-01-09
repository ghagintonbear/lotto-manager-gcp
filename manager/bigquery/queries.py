import os

import google.cloud.bigquery as bq


def run_query(client: bq.Client, query: str, destination_table_name: str) -> None:
    job_config = bq.QueryJobConfig(destination='.'.join([os.getenv("PROJECT_ID"), 'manager', destination_table_name]))
    query_job = client.query(query, job_config=job_config)
    general_summary_job_result = query_job.result()
    print(f'general_summary_job_result: {general_summary_job_result}')
    return


def create_general_summary_query(dataset_ids: list) -> str:
    query_for_all_general_summaries = ',\n'.join([
        _query_for_general_summary(dataset_id) for dataset_id in dataset_ids
    ])
    query_for_appending_tables = ' UNION ALL\n'.join([
        f'SELECT * FROM collapsed_to_one_row_{dataset_id}' for dataset_id in dataset_ids
    ])
    general_summary_query = query_for_all_general_summaries + '\n' + query_for_appending_tables
    print(f'General Summary Query:\n{general_summary_query}')
    return general_summary_query


def _query_for_general_summary(dataset_id: str) -> str:
    return \
        f"""WITH results_with_new_columns AS (
                SELECT Match_Type, '{dataset_id}' AS Play_Date, 
                    CAST(REGEXP_REPLACE(prize, r"[\D]+", "") AS INT64) AS Winnings,
                    (select COUNT(*) from `{dataset_id}.results`) AS Num_of_Players
                FROM `{dataset_id}.results`
            ),
            only_winnings_{dataset_id} AS (
                SELECT *
                FROM results_with_new_columns
                WHERE Winnings > 0
            ),
            collapsed_to_one_row_{dataset_id} AS(
                SELECT DISTINCT Play_Date, Winnings, Num_of_Players, 
                        ((select STRING_AGG(Match_Type, '; ') from `only_winnings_{dataset_id}`)) AS Winning_Description
                FROM only_winnings_{dataset_id}
            ),
            summary_{dataset_id} AS (
                SELECT Play_Date, Num_of_Players, (Winnings / 100) AS Winnings, 
                (Winnings / (100 * Num_of_Players)) AS Winnings_per_Player, Winning_Description
                FROM collapsed_to_one_row_{dataset_id}
            )"""
