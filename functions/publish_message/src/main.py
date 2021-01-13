import os

import google.cloud.pubsub_v1 as pubsub

from cloud_utils.handle_requests import extract_field_from_request

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
    """ publishes a message to the named topic

        Triggered by http request.

    Args:
         request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
        Required fields in request json:
            - "topic_name" (used as str): name of topic where message will be published
            - "message"    (used as str): message to be published (primarily for logs)
            - "attribute" (used as dict): dict containing additional attributes to be passed
                                          topic subscribers as keyword arguments.
    """
    topic_name = extract_field_from_request(request, 'topic_name')
    message = extract_field_from_request(request, 'message')
    attributes = extract_field_from_request(request, 'attributes')

    # References an existing topic
    topic_path = publisher.topic_path(gcp_project_id, topic_name)

    # message must be byte string
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
