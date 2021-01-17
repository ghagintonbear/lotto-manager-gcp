from manager.bigquery.write import create_bigquery_dataset, write_dataframe_to_bigquery
from manager.bigquery.read import get_dataset_ids_with_results
from manager.bigquery.queries import run_query, create_general_summary_query, create_player_summary_query


class TestBigqueryWrite:
    dataset_a = '1234_56_78_test_a'

    def test_create_bigquery_dataset(self, bigquery_client):
        dataset_name = self.dataset_a

        result = create_bigquery_dataset(bigquery_client, dataset_name)

        dataset_list = bigquery_client.list_datasets(max_results=3)

        assert dataset_name in [dataset.dataset_id for dataset in dataset_list]
        assert result == f"Created dataset {bigquery_client.project}.{dataset_name}"

    def test_create_bigquery_dataset_does_nothing_if_exists(self, bigquery_client):
        dataset_name = self.dataset_a

        result = create_bigquery_dataset(bigquery_client, dataset_name)

        assert result == f"Dataset {bigquery_client.project}.{dataset_name} already exists"

    def test_write_dataframe_to_bigquery(self, bigquery_client, helpers, results_b):
        dataset_name = self.dataset_a
        table_name = 'results'
        project_id = bigquery_client.project

        result = write_dataframe_to_bigquery(bigquery_client, data=results_b,
                                             table_name=table_name, dataset_name=dataset_name)

        assert result == f"Loaded 3 rows and 5 columns to {'.'.join([project_id, dataset_name, table_name])}"
        helpers.assert_bigquery_table_equal_to_dataframe(bigquery_client, dataset_name, table_name, expected=results_b)

    def test_write_dataframe_to_bigquery_overwrites_if_exists(self, bigquery_client, helpers, results_a):

        dataset_name = self.dataset_a
        table_name = 'results'
        project_id = bigquery_client.project

        result = write_dataframe_to_bigquery(bigquery_client, data=results_a,
                                             table_name=table_name, dataset_name=dataset_name)

        assert result == f"Loaded 3 rows and 5 columns to {'.'.join([project_id, dataset_name, table_name])}"
        helpers.assert_bigquery_table_equal_to_dataframe(bigquery_client, dataset_name, table_name, expected=results_a)


class TestBigqueryQueries:
    manager_dataset_name = 'test_manager'

    def test_create_general_summary_query(self, bigquery_client, helpers, expected_general_summary_with_ab, results_b):
        # setup for this class
        helpers.create_dataset_test_manager(bigquery_client)
        # set up for this test
        helpers.create_dataset_X_and_upload_results_X(bigquery_client, x='b', results=results_b)

        dataset_ids = get_dataset_ids_with_results(bigquery_client, pattern=r'\d{4}_\d{2}_\d{2}_test_\w')
        general_summary_query = create_general_summary_query(dataset_ids)
        destination_table_name = 'test_general_summary'

        run_query(
            client=bigquery_client,
            query=general_summary_query,
            destination_table_name=destination_table_name,
            destination_dataset_name=self.manager_dataset_name
        )

        helpers.assert_bigquery_table_equal_to_dataframe(
            bigquery_client, dataset_name=self.manager_dataset_name, table_name=destination_table_name,
            expected=expected_general_summary_with_ab
        )

    def test_create_player_summary_query(self, bigquery_client, helpers, expected_player_summary_with_ab):

        dataset_ids = get_dataset_ids_with_results(bigquery_client, pattern=r'\d{4}_\d{2}_\d{2}_test_\w')
        player_summary_query = create_player_summary_query(dataset_ids)
        destination_table_name = 'test_player_summary'

        run_query(
            client=bigquery_client,
            query=player_summary_query,
            destination_table_name=destination_table_name,
            destination_dataset_name=self.manager_dataset_name
        )

        helpers.assert_bigquery_table_equal_to_dataframe(
            bigquery_client, dataset_name=self.manager_dataset_name, table_name=destination_table_name,
            expected=expected_player_summary_with_ab, sort_by='Name'
        )

    def test_with_new_table_create_new_summary_and_overwrite_old(
            self, bigquery_client, helpers, results_c, expected_general_summary_with_abc
    ):
        # run set up for this test
        helpers.create_dataset_X_and_upload_results_X(bigquery_client, x='c', results=results_c)

        dataset_ids = get_dataset_ids_with_results(bigquery_client, pattern=r'\d{4}_\d{2}_\d{2}_test_\w')
        general_summary_query = create_general_summary_query(dataset_ids)
        destination_table_name = 'test_general_summary'

        run_query(
            client=bigquery_client,
            query=general_summary_query,
            destination_table_name=destination_table_name,
            destination_dataset_name=self.manager_dataset_name
        )

        helpers.assert_bigquery_table_equal_to_dataframe(
            bigquery_client, dataset_name=self.manager_dataset_name, table_name=destination_table_name,
            expected=expected_general_summary_with_abc
        )
