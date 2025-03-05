from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices


class TelemetreeConfig(BaseModel):
    """
    Configuration class for Telemetree.

    Attributes:
        public_key (str): The public key used for encryption.
        host (str): The host URL for the Telemetree service.
    """

    public_key: str = Field(..., description="The RSA public key used for encryption")
    host: str = Field(
        ..., description="The host URL for the Telemetree pipeline service"
    )


class EncryptedEvent(BaseModel):
    """
    Class representing an encrypted event.

    Attributes:
        key (str): The encrypted key used for decryption.
        iv (str): The encrypted initialization vector used for decryption.
        body (str): The encrypted event data.
    """

    key: str
    iv: str
    body: str


class Event(BaseModel):
    """
    Represents an event to be tracked.

    Attributes:
        - Required:
            - event_type (str): The type of event to track.
            - telegram_id (int): The Telegram ID of the user.
        - Optional:
            - is_premium (Optional[bool]): The premium status of the user.
            - username (Optional[str]): The username of the user.
            - firstname (Optional[str]): The first name of the user.
            - lastname (Optional[str]): The last name of the user.
            - language (Optional[str]): The language of the user.
            - referrer_type (Optional[str]): The referrer type.
            - referrer (Optional[int]): The referrer.
        - Default:
            - event_source (str): The event source.
            - datetime (str): The event timestamp in ISO 8601 format.
            - session_id (int): The session ID.
    """

    event_type: str = Field(
        ...,
        description="Required. The type of event to track",
        max_length=255,
        alias="event_name",
        validation_alias=AliasChoices("event_name", "event_type"),
    )
    telegram_id: int = Field(
        ...,
        gt=0,
        description="Required. The Telegram ID of the user",
        alias="user_id",
        validation_alias=AliasChoices("user_id", "telegram_id"),
    )

    # Optional fields
    is_premium: Optional[bool] = Field(
        default=False, description="Optional. The premium status of the user"
    )
    username: Optional[str] = Field(
        default=None, description="Optional. The username of the user"
    )
    firstname: Optional[str] = Field(
        default=None, max_length=255, description="Optional. The first name of the user"
    )
    lastname: Optional[str] = Field(
        default=None, max_length=255, description="Optional. The last name of the user"
    )
    language: Optional[str] = Field(
        default=None, max_length=5, description="Optional. IETF language tag"
    )
    referrer_type: Optional[str] = Field(
        default="backend", max_length=255, description="Optional. Traffic source type"
    )
    referrer: Optional[int] = Field(
        default=0, description="Optional. Telegram chat_instance referrer"
    )

    # Default fields
    event_source: str = Field(
        default="python_SDK", max_length=255, description="Default. Event source"
    )
    datetime: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Default. Event timestamp in ISO 8601 format",
    )
    session_id: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000),
        description="Default. Session ID",
    )

    application_id: Optional[str] = Field(
        default=None, description="Optional. The application ID"
    )
