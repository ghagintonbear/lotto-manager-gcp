import base64
from datetime import datetime, date

from manager.bigquery import read_selected_numbers, establish_results_in_bigquery
from manager.check_matches import collect_winning_numbers, check_matches_on_selected
from manager.scrape_results import scrape_historical_results, scrape_prize_breakdown, extract_draw_result
from manager.tools import get_last_friday_date


def run_manager(event, _context):
    """Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         _context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time. Both type str
    """
    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        print(f'PubSub event: "{pubsub_message}"')

    if 'attributes' in event:
        print(f'PubSub attributes: attributes={event["attributes"]}')
        if 'run_date' in event["attributes"]:
            run_date_str = event["attributes"]['run_date']
            run_date = datetime.strptime(run_date_str, '%Y-%m-%d')
        else:
            run_date = datetime.now().date()

    selected = read_selected_numbers()

    draw_date, draw_date_str = get_last_friday_date(run_date)

    draw_result, prize_breakdown = get_draw_information(draw_date)
    winning_numbers = collect_winning_numbers(draw_result)

    results = check_matches_on_selected(selected, winning_numbers, prize_breakdown)

    establish_results_in_bigquery(
        dataset_name=draw_date_str,
        results=results, draw_result=draw_result, prize_breakdown=prize_breakdown
    )

    return 'Completed'


def get_draw_information(draw_date: date) -> (dict, dict):
    historical_data = scrape_historical_results()
    draw_result = extract_draw_result(draw_date, historical_data)
    prize_breakdown = scrape_prize_breakdown(draw_result['DrawNumber'])
    return draw_result, prize_breakdown
