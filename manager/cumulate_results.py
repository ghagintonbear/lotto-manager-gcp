import glob

import pandas as pd


def compute_cumulated_result(path_to_results='.\\result_archive\\*\\*.xlsx'):
    """ Iterates over all .xlsx files in results_archive to produce bespoke summary tables requested by user. """
    general_overview = {}
    player_prize_breakdown = {}
    for xlsx_file_path in glob.glob(path_to_results):
        _, play_interval, filename = xlsx_file_path.rsplit('\\', maxsplit=2)
        play_date = filename.rsplit('.', maxsplit=1)[0]
        result = pd.read_excel(xlsx_file_path, sheet_name='Result', engine='openpyxl')
        result['Prize'] = result['Prize'].str.replace('£', '').astype(float)

        general_overview = calculate_general_overview_row(
            data=result, store=general_overview, play_interval=play_interval, play_date=play_date
        )

        player_prize_breakdown = calculate_player_prize_breakdown(
            data=result, store=player_prize_breakdown, play_interval=play_interval, play_date=play_date
        )

    player_prize_breakdown.pop('players')  # side effect of calculate_player_prize_breakdown

    return pd.DataFrame(general_overview), pd.DataFrame(player_prize_breakdown)


def calculate_general_overview_row(data: pd.DataFrame, store: dict, play_interval: str, play_date: str) -> dict:
    """ Bespoke logic to generate consecutive rows of general summary results from each play date.
    Keys of dictionary are:
        * Interval - list of interval values which play date falls into
        * Play Date - list of draw dates in string format
        * Winnings - list of total prize money won on given draw
        * Num of Players - list of the number of players on given draw
        * Winning Description - list of types of matches achieved on given draw
    """
    store['Interval'] = store.get('Interval', []) + [play_interval]
    store['Play Date'] = store.get('Play Date', []) + [play_date]
    store['Winnings'] = store.get('Winnings', []) + [data['Prize'].sum()]
    store['Num of Players'] = store.get('Num of Players', []) + [data.shape[0]]
    store['Winning per Person'] = store.get('Winning per Person', []) + [
        store['Winnings'][-1] / store['Num of Players'][-1]
    ]
    store['Winning Description'] = store.get('Winning Description', []) + [
        data[data['Prize'] > 0]['Match Type'].str.cat(sep='; ')
    ]

    return store


def calculate_player_prize_breakdown(data: pd.DataFrame, store: dict, play_interval: str, play_date: str) -> dict:
    """ Bespoke logic to generate consecutive rows of prize received per player. Keys of dictionary are:
        * players - set of all players to have every played
        * Interval - list of interval values which play date falls into
        * Play Date - list of draw dates in string format
        * <Player Name> - list of prize money won per player on given `play_date`
    """
    store['players'] = set(store.get('players', [])).union(data['Name'].values)
    store['Interval'] = store.get('Interval', []) + [play_interval]
    store['Play Date'] = store.get('Play Date', []) + [play_date]
    expected_length = len(store['Play Date']) - 1
    for player in store['players']:
        current_length = len(store.get(player, []))
        if current_length != expected_length:
            store[player] = store.get(player, []) + [None] * (expected_length - current_length)

        if player in data['Name'].values:
            value = data['Prize'].sum()/data.shape[0]
        else:
            value = None

        store[player] = store.get(player, []) + [value]

    return store
