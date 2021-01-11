import os

import google.cloud.bigquery as bq


def run_query(client: bq.Client, query: str, destination_table_name: str) -> None:
    job_config = bq.QueryJobConfig(
        destination='.'.join([os.getenv("PROJECT_ID"), 'manager', destination_table_name]),
        write_disposition='WRITE_TRUNCATE'
    )
    query_job = client.query(query, job_config=job_config)
    general_summary_job_result = query_job.result()
    print(f'general_summary_job_result completed?: {bool(general_summary_job_result)}')
    return


def create_general_summary_query(dataset_ids: [str]) -> str:
    query_for_all_general_summaries = ',\n'.join([
        _query_for_general_summary(dataset_id) for dataset_id in dataset_ids
    ])
    query_for_appending_summaries = ' UNION ALL\n'.join([
        f'SELECT * FROM summary_{dataset_id}' for dataset_id in dataset_ids
    ])
    general_summary_query = 'WITH ' + query_for_all_general_summaries + '\n' + query_for_appending_summaries \
                            + '\n ORDER BY Play_Date'

    return general_summary_query


def create_player_summary_query(dataset_ids: [str]) -> str:
    query_for_all_player_summaries = '\nUNION ALL\n'.join([
        _query_for_player_summary(dataset_id) for dataset_id in dataset_ids
    ])
    player_summary_query = \
        f"""WITH all_player_summaries AS (
            {query_for_all_player_summaries}
            )
            SELECT Name, SUM(Winnings_per_Player)
            FROM all_player_summaries
            GROUP BY Name
        """

    return player_summary_query


def _query_for_general_summary(dataset_id: str) -> str:
    """
    * results_with_new_columns:
        select columns of interest and create Play_Date col
        convert Prize (type string, [£,.0-9]) to int to avoid rounding errors
        add Num_of_Players which is the length of the data by design

    * filtered_match_types - helper query

    * winning_match_types -> 1x1 table:
        EXISTS checks if query result is empty or not
        It only returns True or False

    * collapsed_to_one_row -> 4x1 table:
        aggregates results

    * summary:
        converts ints (pence) into float (pounds) after aggregation
    """
    return \
        f"""results_with_new_columns_{dataset_id} AS (
                SELECT Match_Type, '{dataset_id}' AS Play_Date,
                    CAST(REGEXP_REPLACE(Prize, r"[\D]+", "") AS INT64) AS Winnings,
                    (select COUNT(*) from `{dataset_id}.results`) AS Num_of_Players
                FROM `{dataset_id}.results`
            ),
            filtered_match_types_{dataset_id} AS (
                SELECT Match_Type 
                FROM results_with_new_columns_{dataset_id}
                WHERE Winnings > 0
            ),
            winning_match_types_{dataset_id} AS (
                SELECT
                    CASE 
                    WHEN EXISTS(SELECT Match_Type FROM filtered_match_types_{dataset_id})
                      THEN STRING_AGG(Match_Type, '; ')
                      ELSE NULL
                    END AS Winning_Match_Type
                FROM filtered_match_types_{dataset_id}
            ),
            collapsed_to_one_row_{dataset_id} AS(
                SELECT DISTINCT Play_Date, Num_of_Players, 
                                (SELECT Winning_Match_Type FROM winning_match_types_{dataset_id}) AS Winning_Match_Type,
                                (SELECT SUM(Winnings) AS Total_Winnings FROM results_with_new_columns_{dataset_id}) AS Total_Winnings
                FROM results_with_new_columns_{dataset_id}
            ),
            summary_{dataset_id} AS (
                SELECT Play_Date, Num_of_Players, (Total_Winnings / 100) AS Total_Winnings, 
                (Total_Winnings / (100 * Num_of_Players)) AS Winnings_per_Player, Winning_Match_Type
                FROM collapsed_to_one_row_{dataset_id}
            )"""


def _query_for_player_summary(dataset_id: str) -> str:
    """
    Insert dataset_id as Play_Date,
    Select Name,
    Compute Winnings per player
    """
    return \
        f"""SELECT '{dataset_id}' AS Play_Date, Name, 
                    ((SELECT SUM(CAST(REGEXP_REPLACE(Prize, r"[\D]+", "") AS INT64)) FROM `{dataset_id}.results`)/
                     (100 * (SELECT COUNT(*) FROM `{dataset_id}.results`))
                    ) AS Winnings_per_Player
            FROM `{dataset_id}.results`"""
