import os

import google.cloud.bigquery as bq


def get_selected_numbers(_path: str = 'selected.numbers'):
    # TODO: GCP read from BigQuery
    """ validates Selected Numbers. Ensures numbers selected are valid and there are no duplicates in Name col."""
    bq_client = bq.Client()
    select_all_query = f"""
    SELECT *
    FROM `{os.getenv('PROJECT_ID')}.selected.numbers`
    """
    selected_numbers = (
        bq_client.query(select_all_query) \
            .result()\
            .to_dataframe()
    )
    bq_client.query()
    # query bq,
    # convert to dataframe
    # perform checks
    pass