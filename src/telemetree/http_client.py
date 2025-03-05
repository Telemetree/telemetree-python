from enum import Enum
from socket import timeout
import logging

import requests

from telemetree.constants import HTTP_TIMEOUT
from telemetree.exceptions import WrongIdentityKeys
from telemetree.schemas import EncryptedEvent

logger = logging.getLogger("telemetree.http_client")


class HttpStatus(Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class HttpClient:
    def __init__(self, api_key: str, project_id: str) -> None:
        self.api_key = api_key
        self.project_id = project_id

    def get(self, config_url: str):
        """
        Sends a GET request to the specified URL with the given headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        url = f"{config_url}?project={self.project_id}"

        request = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response_json = request.json()
        if request.status_code != HttpStatus.OK.value:
            logger.error(
                "Failed to fetch the config. Status code: %s. Response: %s",
                request.status_code,
                response_json,
            )
            raise WrongIdentityKeys(
                f"Failed to fetch the config. Status code: {request.status_code}. Response: {response_json}"
            )

        return response_json

    def post(self, data: EncryptedEvent, url: str):
        """
        Sends a POST request to the specified URL with the given data and headers.

        Args:
            url: The URL to send the event request to.
            data (EncryptedEvent): The data to be sent in the request body.

        Returns:
            HTTPResponse: The response object returned by the server.

        Raises:
            HTTPError: If an HTTP error occurs during the request.
            URLError: If a URL error occurs during the request.
            timeout: If the request times out.
        """
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "x-project-id": self.project_id,
            }

            response = requests.post(url, json=data.model_dump(), headers=headers, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
            timeout,
        ) as e:
            logger.exception("Failed to send POST request: %s", e)
            raise e
