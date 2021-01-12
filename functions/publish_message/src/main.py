import os

import google.cloud.pubsub_v1 as pubsub

from cloud_utils.handle_requests import extract_field_from_request
from cloud_utils.logging import cloud_log

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
        cloud_log(f'Message {message} published.')
        return 'Successfully Published'
    except Exception as e:
        cloud_log(repr(e), 'error')
        return e, 500
