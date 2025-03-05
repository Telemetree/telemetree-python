import base64
import json
import logging
from typing import Optional, Union

from pydantic import ValidationError

from telemetree.config import Config
from telemetree.http_client import HttpClient
from telemetree.schemas import EncryptedEvent, Event
from telemetree.encryption import EncryptionService
from telemetree.utils import validate_uuid


logger = logging.getLogger("telemetree.client")


class Telemetree:
    def __init__(self, api_key: str, project_id: str):
        """
        Initializes the TelemetreeClient with the provided API key and project ID.

        Args:
            api_key (str): The API key for authentication.
            project_id (str): The project ID for the Telemetree service.
        """
        self.api_key = validate_uuid(api_key)
        self.project_id = validate_uuid(project_id)

        self.http_client = HttpClient(self.api_key, self.project_id)

        self.config = Config(self.http_client)
        self.public_key = self.config.get_public_key()
        self.host = self.config.get_host()

        self.encryption_service = EncryptionService(self.public_key)

    def track(self, event: Union[Event, dict]) -> dict:
        """Key function to track events.

        Args:
            event (Union[Event, dict]): The event to track.

        Required:
            - event_type (str): The type of event to track.
            - telegram_id (int): The Telegram ID of the user.
        Optional:
            - is_premium (bool): The premium status of the user.
            - username (str): The username of the user.
            - firstname (str): The first name of the user.
            - lastname (str): The last name of the user.
            - language (str): The language of the user.
            - referrer_type (str): The referrer type.
            - referrer (int): The referrer.

        Raises:
            ValueError: If the event is invalid.

        Returns:
            dict: The response from the server.
        """
        if not isinstance(event, Event) and not isinstance(event, dict):
            logger.error("Invalid type: expected Event type or dictionary")
            raise ValueError("Invalid type: expected Event type or dictionary")
        if isinstance(event, dict):
            try:
                event = Event(**event)
            except ValidationError as e:
                logger.error("Invalid event: %s", e)
                raise ValueError(f"Invalid event: {e}") from e

        stringified_event = event.model_dump_json()
        encrypted_event = self.encryption_service.encrypt(stringified_event)
        encrypted_event = EncryptedEvent(
            key=encrypted_event["key"].decode("utf-8"),
            iv=encrypted_event["iv"].decode("utf-8"),
            body=encrypted_event["body"].decode("utf-8"),
        )

        return self.http_client.post(encrypted_event, self.host)
