import os
from typing import Literal

from google.cloud.logging import Resource, Client

resource = Resource(type="cloud_function", labels={"user_defined": "us-central1-a"})

logging_client = Client()
cloud_logger = logging_client.logger(os.getenv('PROJECT_ID'))


def cloud_log(message: str, level: str = Literal['info', 'warning', 'error']) -> None:
    cloud_logger.log_struct({'level': level, 'message': message}, resource=resource)

    return
