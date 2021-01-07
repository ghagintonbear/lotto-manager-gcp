import pandas as pd


def collect_winning_numbers(results: dict) -> dict:
    """ results dict has 1 ball number per key. this helper func collects ball numbers and lucky star
        numbers into their respective lists and packages them into a new dict.
    """
    winning = {}
    for key, value in results.items():
        if key.startswith('Ball') or key.startswith('Lucky Star'):
            new_key = key.rsplit(' ', maxsplit=1)[0] + 's'
            winning[new_key] = winning.get(new_key, []) + [value]

    return winning


def match_type_label(row: pd.Series) -> str:
    """ recreates the match type label you see on the prize breakdown table e.g. Match 5 + 2 Stars, based on
        how many matches accomplished.
    """
    ball_match = row['Balls_Matched']
    star_match = row['Stars_Matched']
    if ball_match == 0 or star_match == 0:
        return 'Match ' + str(ball_match)
    elif ball_match > 0 and star_match == 1:
        return 'Match ' + str(ball_match) + ' + ' + str(star_match) + ' Star'
    elif ball_match > 0 and star_match == 2:
        return 'Match ' + str(ball_match) + ' + ' + str(star_match) + ' Stars'


def check_matches_on_selected(selected: pd.DataFrame, winning: dict, prize_breakdown: dict) -> pd.DataFrame:
    """ Performs operations on selected DataFrame to determine:
        * how many balls and stars matched
        * match type label achieved, e.g. Match 5 + 2 Stars
        * the respective winnings associated with the match type label.
    """
    number_cols = [col for col in selected.columns if col.startswith('Number')]
    star_cols = [col for col in selected.columns if col.startswith('Lucky_Star')]

    selected['Balls_Matched'] = selected.loc[:, number_cols].isin(winning['Balls']).sum(axis=1)
    selected['Stars_Matched'] = selected.loc[:, star_cols].isin(winning['Lucky Stars']).sum(axis=1)
    selected['Match_Type'] = selected[['Balls_Matched', 'Stars_Matched']].apply(match_type_label, axis=1)
    selected['Prize'] = selected['Match_Type'].map(prize_breakdown).fillna('£0.00')

    return selected
