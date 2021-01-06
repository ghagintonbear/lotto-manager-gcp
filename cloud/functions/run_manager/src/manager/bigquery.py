import os

import pandas as pd

from manager.tools import assert_values_in_range


def get_selected_numbers():
    """ validates Selected Numbers. Ensures numbers selected are valid and there are no duplicates in Name col."""
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
