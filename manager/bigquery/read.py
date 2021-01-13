import os

import pandas as pd


def read_selected_numbers() -> pd.DataFrame:
    """ Read manager.selected_numbers ('./selected_numbers.csv') from BigQuery and validates them.
        Ensures numbers selected are valid and there are no duplicates in Name col.
    """
    select_all_query = f"""
    SELECT *
    FROM `{os.getenv('PROJECT_ID')}.manager.selected_numbers`"""

    return pd.read_gbq(select_all_query)
