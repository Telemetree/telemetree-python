import base64
import json
import logging
from typing import Optional, Union, Dict, Any

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

    def _is_telegram_webhook(self, data: dict) -> bool:
        """
        Detect if the given data is a Telegram webhook payload.
        
        Args:
            data (dict): The data to check.
            
        Returns:
            bool: True if the data is a Telegram webhook payload, False otherwise.
        """
        # Check for typical Telegram webhook fields
        return "update_id" in data and any([
            "message" in data,
            "edited_message" in data,
            "channel_post" in data,
            "edited_channel_post" in data,
            "inline_query" in data,
            "chosen_inline_result" in data,
            "callback_query" in data,
            "shipping_query" in data,
            "pre_checkout_query" in data,
            "poll" in data,
            "poll_answer" in data,
            "my_chat_member" in data,
            "chat_member" in data,
            "chat_join_request" in data
        ])
    
    def _transform_telegram_webhook(self, data: dict) -> dict:
        """
        Transform Telegram webhook data into Telemetree Event format.
        
        Args:
            data (dict): The Telegram webhook data.
            
        Returns:
            dict: The transformed data in Telemetree Event format.
        """
        event_type = "telegram_webhook"
        user_id = None
        user_data = {}
        
        # Extract user_id and event_type based on update type
        if "message" in data and "from" in data["message"]:
            event_type = "telegram_message"
            user_data = data["message"]["from"]
        elif "edited_message" in data and "from" in data["edited_message"]:
            event_type = "telegram_edited_message"
            user_data = data["edited_message"]["from"]
        elif "channel_post" in data and "from" in data["channel_post"]:
            event_type = "telegram_channel_post"
            user_data = data["channel_post"]["from"]
        elif "edited_channel_post" in data and "from" in data["edited_channel_post"]:
            event_type = "telegram_edited_channel_post"
            user_data = data["edited_channel_post"]["from"]
        elif "inline_query" in data and "from" in data["inline_query"]:
            event_type = "telegram_inline_query"
            user_data = data["inline_query"]["from"]
        elif "chosen_inline_result" in data and "from" in data["chosen_inline_result"]:
            event_type = "telegram_chosen_inline_result"
            user_data = data["chosen_inline_result"]["from"]
        elif "callback_query" in data and "from" in data["callback_query"]:
            event_type = "telegram_callback_query"
            user_data = data["callback_query"]["from"]
        elif "shipping_query" in data and "from" in data["shipping_query"]:
            event_type = "telegram_shipping_query"
            user_data = data["shipping_query"]["from"]
        elif "pre_checkout_query" in data and "from" in data["pre_checkout_query"]:
            event_type = "telegram_pre_checkout_query"
            user_data = data["pre_checkout_query"]["from"]
        elif "poll_answer" in data and "user" in data["poll_answer"]:
            event_type = "telegram_poll_answer"
            user_data = data["poll_answer"]["user"]
        elif "my_chat_member" in data and "from" in data["my_chat_member"]:
            event_type = "telegram_my_chat_member"
            user_data = data["my_chat_member"]["from"]
        elif "chat_member" in data and "from" in data["chat_member"]:
            event_type = "telegram_chat_member"
            user_data = data["chat_member"]["from"]
        elif "chat_join_request" in data and "from" in data["chat_join_request"]:
            event_type = "telegram_chat_join_request"
            user_data = data["chat_join_request"]["from"]
        
        # Extract user_id from user_data
        if user_data and "id" in user_data:
            user_id = user_data["id"]
        
        # Create transformed data
        transformed_data = {
            "event_type": event_type,
            "telegram_id": user_id,
        }
        
        # Add optional user data if available
        if user_data:
            if "username" in user_data:
                transformed_data["username"] = user_data["username"]
            if "first_name" in user_data:
                transformed_data["firstname"] = user_data["first_name"]
            if "last_name" in user_data:
                transformed_data["lastname"] = user_data["last_name"]
            if "language_code" in user_data:
                transformed_data["language"] = user_data["language_code"]
            if "is_premium" in user_data:
                transformed_data["is_premium"] = user_data["is_premium"]
        
        # Add original data as application_id for reference
        transformed_data["application_id"] = json.dumps({"update_id": data.get("update_id")})
        
        return transformed_data
    
    def track(self, event: Union[Event, dict]) -> dict:
        """Key function to track events.

        Args:
            event (Union[Event, dict]): The event to track.
            
            If a dictionary is provided, it can be:
            1. A pre-formatted Telemetree event with required fields
            2. A raw Telegram webhook payload (will be automatically transformed)

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
        
        # Check if this is a Telegram webhook and transform it if needed
        if isinstance(event, dict) and self._is_telegram_webhook(event):
            logger.info("Detected Telegram webhook payload, transforming to Telemetree format")
            event = self._transform_telegram_webhook(event)
        
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
