import pandas as pd


def collect_numbers(results: dict) -> (list, list):
    winning_balls = []
    lucky_stars = []
    for key, value in results.items():
        if key.startswith('Ball'):
            winning_balls.append(value)
        elif key.startswith('Lucky Star'):
            lucky_stars.append(value)

    return winning_balls, lucky_stars


def match_type_label(row: pd.Series) -> str:
    ball_match = row['ball_match']
    star_match = row['star_match']
    if ball_match == 0 or star_match == 0:
        return 'Match ' + str(ball_match)
    elif ball_match > 0 and star_match == 1:
        return 'Match ' + str(ball_match) + ' + ' + str(star_match) + ' Star'
    elif ball_match > 0 and star_match == 2:
        return 'Match ' + str(ball_match) + ' + ' + str(star_match) + ' Stars'


def check_numbers(selected: pd.DataFrame, winning: list, stars: list, prize_breakdown: dict) -> pd.DataFrame:
    number_cols = [col for col in selected.columns if col.startswith('Number')]
    star_cols = [col for col in selected.columns if col.startswith('Lucky Stars')]

    selected['Balls Matched'] = selected.loc[:, number_cols].isin(winning).sum(axis=1)
    selected['Stars Matched'] = selected.loc[:, star_cols].isin(stars).sum(axis=1)
    selected['Match Type'] = selected[['Balls Matched', 'Stars Matched']].apply(match_type_label, axis=1)
    selected['prize'] = selected['match_type'].map(prize_breakdown).fillna('£0.00')

    return selected
