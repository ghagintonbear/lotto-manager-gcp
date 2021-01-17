from unittest.mock import MagicMock, patch

from manager.bigquery.read import get_dataset_ids_with_results


def mock_list_datasets():
    class MockDataset:
        def __init__(self, dataset_id):
            self.dataset_id = dataset_id

    all_dataset_ids = [
        '2020_01_01_valid', '2O2O_O1_O1_inva@ld', '2020_012_01_invalid',
        '2020_02_02_valid', '2020_03_03_valid', '2020_01_01', 'manager'
    ]

    return [MockDataset(dataset_id) for dataset_id in all_dataset_ids]


def mock_list_tables(dataset):
    class MockTable:
        def __init__(self, table_id):
            self.table_id = table_id

    def to_mock_table_list(table_id_list):
        return [MockTable(table_id) for table_id in table_id_list]

    return {
        '2020_01_01_valid': to_mock_table_list(['results', 'other']),
        '2020_02_02_valid': to_mock_table_list(['other', 'results']),
        '2020_03_03_valid': to_mock_table_list(['not_results', 'other']),
    }[dataset]


def test_get_dataset_ids_with_results():  # bigquery/read.py
    expected_dataset_ids = ['2020_01_01_valid', '2020_02_02_valid']

    mock_client = MagicMock()
    mock_client.list_datasets.side_effect = mock_list_datasets
    mock_client.list_tables.side_effect = mock_list_tables

    with patch('google.cloud.bigquery.Client', mock_client) as mock_client:
        results = get_dataset_ids_with_results(mock_client)
        assert results == expected_dataset_ids
