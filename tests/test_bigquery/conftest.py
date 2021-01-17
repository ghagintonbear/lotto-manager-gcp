import pandas as pd
from google.cloud.bigquery import Client
from pandas.testing import assert_frame_equal
from pytest import fixture

dataset_names = {
    'a': '1234_56_78_test_a',
    'b': '1234_56_78_test_b',
    'c': '1234_56_78_test_c',
}


@fixture(scope='session')
def bigquery_client():
    """ Sets up google.cloud.bigquery Client for test session. Once yielded, perform teardown actions. """
    client = Client()

    yield client

    print('Session Finished, Deleting all test datasets and tables.')
    datasets_to_delete = list(dataset_names.values()) + ['test_manager']
    for dataset_name in datasets_to_delete:
        dataset_reference = client.project + '.' + dataset_name
        client.delete_dataset(dataset_reference, delete_contents=True, not_found_ok=True)


@fixture(scope='session')
def helpers():
    """ Provides access to various helper functions. """
    return Helpers()


class Helpers:
    @staticmethod
    def assert_bigquery_table_equal_to_dataframe(
            client: Client, dataset_name: str, table_name: str, expected: pd.DataFrame, sort_by: str = ''
    ) -> None:
        # get data from bigquery
        query_job = client.query(f"SELECT * FROM `{client.project}.{dataset_name}.{table_name}`")
        results = query_job.result()  # Waits for job to complete.
        results_df = results.to_dataframe()

        if sort_by:
            results_df = results_df.sort_values(by=sort_by).reset_index(drop=True)
            expected = expected.sort_values(by=sort_by).reset_index(drop=True)

        assert_frame_equal(results_df, expected)

    @staticmethod
    def create_dataset_test_manager(client: Client):
        from manager.bigquery.write import create_bigquery_dataset

        create_bigquery_dataset(client, 'test_manager')

    @staticmethod
    def create_dataset_X_and_upload_results_X(client: Client, x: str, results: pd.DataFrame):
        from manager.bigquery.write import create_bigquery_dataset, write_dataframe_to_bigquery

        dataset_name = dataset_names[x]
        create_bigquery_dataset(client, dataset_name)
        write_dataframe_to_bigquery(client, data=results, table_name='results', dataset_name=dataset_name)


@fixture(scope='session')
def results_a():
    return pd.DataFrame({
        'Name': ['Michele', 'Vanessa', 'Kobe'],
        'Balls_Matched': [2, 3, 4], 'Stars_Matched': [0, 0, 0],
        'Match_Type': ['Match 2', 'Match 3', 'Match 4'],
        'Prize': ['£2.50', '£5.90', '£25.50']
    })


@fixture(scope='session')
def results_b():
    return pd.DataFrame({
        'Name': ['Michele', 'Lebron', 'Kobe'],
        'Balls_Matched': [1, 2, 0], 'Stars_Matched': [2, 0, 0],
        'Match_Type': ['Match 1 + 2 Stars', 'Match 2', 'Match 0'],
        'Prize': ['£4.90', '£2.50', '£0.00']
    })


@fixture(scope='session')
def results_c():
    return pd.DataFrame({
        'Name': ['Michele', 'Barak'],
        'Balls_Matched': [0, 5], 'Stars_Matched': [2, 5],
        'Match_Type': ['Match 0', 'Match 5 + 2 Stars'],
        'Prize': ['£0.00', '£50,129,756.00']
    })


@fixture(scope='session')
def expected_general_summary_with_ab():
    return pd.DataFrame({
        'Play_Date': [dataset_names['a'], dataset_names['b']],
        'Num_of_Players': [3, 3],
        'Total_Winnings': [33.9, 7.4],
        'Winnings_per_Player': [11.3, 7.4 / 3],
        'Winning_Match_Type': ['Match 2; Match 3; Match 4', 'Match 1 + 2 Stars; Match 2']
    })


@fixture(scope='session')
def expected_player_summary_with_ab():
    return pd.DataFrame({
        'Name': ['Michele', 'Vanessa', 'Kobe', 'Lebron'],
        'Total_Cumulated_Winnings': [413 / 30, 11.3, 413 / 30, 7.4 / 3],
        'Days_Played': [2, 1, 2, 1]
    })


@fixture(scope='session')
def expected_general_summary_with_abc():
    return pd.DataFrame({
        'Play_Date': dataset_names.values(),
        'Num_of_Players': [3, 3, 2],
        'Total_Winnings': [33.9, 7.4, 50129756],
        'Winnings_per_Player': [11.3, 7.4 / 3, 25064878],
        'Winning_Match_Type': ['Match 2; Match 3; Match 4', 'Match 1 + 2 Stars; Match 2', 'Match 5 + 2 Stars']
    })
