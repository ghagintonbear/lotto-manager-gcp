import os
from typing import Union

import google.cloud.pubsub_v1 as pubsub

""" Example JSON trigger:
{
  "topic_name": "scheduled-weekly-9am",
  "message": "service asked to publish on: 2021-01-07",
  "attributes": {
    "run_date": "2021-01-07",
    "cumulate_results": "True" 
  }
}
"""

# Instantiates a Pub/Sub client
publisher = pubsub.PublisherClient()
gcp_project_id = os.getenv('PROJECT_ID')


# Publishes a message to a Cloud Pub/Sub topic.
def publish_message(request):
    topic_name = extract_field_from_request(request, 'topic_name')
    message = extract_field_from_request(request, 'message')
    attributes = extract_field_from_request(request, 'attributes')

    # References an existing topic
    topic_path = publisher.topic_path(gcp_project_id, topic_name)

    message_bytes = message.encode('utf-8')

    # Publishes a message
    try:
        publish_future = publisher.publish(topic_path, message_bytes, **attributes)
        publish_future.result()  # Verify the publish succeeded
        print(f'Message {message} published.')
        return 'Successfully Published'
    except Exception as e:
        print(e)
        return e, 500


def extract_field_from_request(request, field_name: str) -> Union[str, dict]:
    request_json = request.get_json()
    request_args = request.args

    if request_json and field_name in request_json:
        field_contents = request_json[field_name]
    elif request_args and field_name in request_args:
        field_contents = request_args[field_name]
    else:
        message = f'"{field_name}" not defined via JSON or arguments in http header'
        print(f'ERROR: {message}')
        raise RuntimeError(message)

    return field_contents
