import base64
from datetime import datetime, date

from manager.tools import get_last_friday_date
from manager.scrape_results import scrape_historical_results, scrape_prize_breakdown, extract_draw_result


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

    draw_date, draw_date_str = get_last_friday_date(datetime.now().date())

    draw_result, prize_breakdown = get_draw_information(draw_date)

    return draw_result, prize_breakdown


def get_draw_information(draw_date: date) -> (dict, dict):
    historical_data = scrape_historical_results()
    draw_result = extract_draw_result(draw_date, historical_data)
    prize_breakdown = scrape_prize_breakdown(draw_result['DrawNumber'])
    return draw_result, prize_breakdown
