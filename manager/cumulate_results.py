import glob

import pandas as pd


def compute_cumulative_result(path_to_results='.\\result_archive\\*\\*.xlsx'):
    cumulative = {}
    for xlsx_file_path in glob.glob(path_to_results):
        _, play_interval, filename = xlsx_file_path.rsplit('\\', maxsplit=2)
        play_date = filename.rsplit('.', maxsplit=1)[0]
        result = pd.read_excel(xlsx_file_path, sheet_name='Result', engine='openpyxl')
        result['Prize'] = result['Prize'].str.replace('£', '').astype(float)
        cumulative['Play Date'] = cumulative.get('Play Date', []) + [play_date]
        cumulative['Interval'] = cumulative.get('Interval', []) + [play_interval]
        cumulative['Winnings'] = cumulative.get('Winnings', []) + [result['Prize'].sum()]
        cumulative['Num of Players'] = cumulative.get('Num of Players', []) + [result.shape[0]]
        cumulative['Winning per Person'] = cumulative.get('Winning per Person', []) + [
            cumulative['Winnings'][-1] / cumulative['Num of Players'][-1]
        ]
        cumulative['Cumulative Winnings per Person'] = cumulative.get('Cumulative Winnings per Person', []) + [
            sum(cumulative['Winning per Person'])
        ]
        cumulative['Winning Description'] = cumulative.get('Winning Description', []) + [
            result[result['Prize'] > 0]['Match Type'].str.cat(sep='; ')
        ]
    return cumulative
