import pytest
from unittest.mock import patch, MagicMock
from src.telemetree.client import Telemetree
from telemetree.schemas import Event
import src.test.fixtures as fixtures


@pytest.fixture
def mock_telemetree():
    with patch("src.telemetree.client.HttpClient") as mock_http_client, \
         patch("src.telemetree.client.Config") as mock_config, \
         patch("src.telemetree.client.EncryptionService") as mock_encryption_service:
        
        # Configure mocks
        mock_config_instance = mock_config.return_value
        mock_config_instance.get_public_key.return_value = "mock_public_key"
        mock_config_instance.get_host.return_value = "mock_host"
        
        mock_http_client_instance = mock_http_client.return_value
        mock_http_client_instance.post.return_value = {"status": "success"}
        
        mock_encryption_service_instance = mock_encryption_service.return_value
        mock_encryption_service_instance.encrypt.return_value = {
            "key": b"encrypted_key",
            "iv": b"encrypted_iv",
            "body": b"encrypted_body"
        }
        
        # Create Telemetree instance with mocked dependencies
        # Use valid UUID strings for api_key and project_id
        telemetree = Telemetree(
            api_key="12345678-1234-5678-1234-567812345678", 
            project_id="87654321-4321-8765-4321-876543210987"
        )
        
        # Replace the actual post method with a mock to avoid real HTTP requests
        telemetree.http_client.post = MagicMock(return_value={"status": "success"})
        
        return telemetree


def test_is_telegram_webhook(mock_telemetree):
    """Test the _is_telegram_webhook method with various Telegram update types."""
    # Test with message update
    assert mock_telemetree._is_telegram_webhook(fixtures.message_update_telegram_tracked) is True
    
    # Test with edited message update
    assert mock_telemetree._is_telegram_webhook(fixtures.edited_message_update_tracked) is True
    
    # Test with inline query update
    assert mock_telemetree._is_telegram_webhook(fixtures.inline_query_update_telegram) is True
    
    # Test with chosen inline result update
    assert mock_telemetree._is_telegram_webhook(fixtures.chosen_inline_result_update_telegram) is True
    
    # Test with non-Telegram data
    assert mock_telemetree._is_telegram_webhook({"foo": "bar"}) is False
    assert mock_telemetree._is_telegram_webhook({"event_type": "custom", "telegram_id": 123}) is False


def test_transform_telegram_webhook_message(mock_telemetree):
    """Test the _transform_telegram_webhook method with a message update."""
    transformed = mock_telemetree._transform_telegram_webhook(fixtures.message_update_telegram_tracked)
    
    assert transformed["event_type"] == "telegram_message"
    assert transformed["telegram_id"] == 714862471
    assert transformed["username"] == "candyflipline"
    assert transformed["firstname"] == "Chris"
    assert transformed["language"] == "en"
    assert transformed["is_premium"] is True


def test_transform_telegram_webhook_edited_message(mock_telemetree):
    """Test the _transform_telegram_webhook method with an edited message update."""
    transformed = mock_telemetree._transform_telegram_webhook(fixtures.edited_message_update_tracked)
    
    assert transformed["event_type"] == "telegram_edited_message"
    assert transformed["telegram_id"] == 714862471
    assert transformed["username"] == "candyflipline"
    assert transformed["firstname"] == "Chris"
    assert transformed["language"] == "en"
    assert transformed["is_premium"] is True


def test_transform_telegram_webhook_inline_query(mock_telemetree):
    """Test the _transform_telegram_webhook method with an inline query update."""
    transformed = mock_telemetree._transform_telegram_webhook(fixtures.inline_query_update_telegram)
    
    assert transformed["event_type"] == "telegram_inline_query"
    assert transformed["telegram_id"] == 714862471
    assert transformed["username"] == "candyflipline"
    assert transformed["firstname"] == "Chris"
    assert transformed["language"] == "en"
    assert transformed["is_premium"] is True


def test_transform_telegram_webhook_chosen_inline_result(mock_telemetree):
    """Test the _transform_telegram_webhook method with a chosen inline result update."""
    transformed = mock_telemetree._transform_telegram_webhook(fixtures.chosen_inline_result_update_telegram)
    
    assert transformed["event_type"] == "telegram_chosen_inline_result"
    assert transformed["telegram_id"] == 714862471
    assert transformed["username"] == "candyflipline"
    assert transformed["firstname"] == "Chris"
    assert transformed["language"] == "en"
    assert transformed["is_premium"] is True


def test_track_with_telegram_webhook(mock_telemetree):
    """Test the track method with a Telegram webhook payload."""
    with patch.object(mock_telemetree, '_transform_telegram_webhook', wraps=mock_telemetree._transform_telegram_webhook) as mock_transform:
        result = mock_telemetree.track(fixtures.message_update_telegram_tracked)
        
        # Verify that _transform_telegram_webhook was called
        mock_transform.assert_called_once_with(fixtures.message_update_telegram_tracked)
        
        # Verify that the result is as expected
        assert result == {"status": "success"}


def test_track_with_preformatted_event(mock_telemetree):
    """Test the track method with a pre-formatted event."""
    preformatted_event = {
        "event_type": "custom_event",
        "telegram_id": 123456789,
        "username": "test_user",
        "firstname": "Test",
        "lastname": "User"
    }
    
    with patch.object(mock_telemetree, '_transform_telegram_webhook') as mock_transform:
        result = mock_telemetree.track(preformatted_event)
        
        # Verify that _transform_telegram_webhook was NOT called
        mock_transform.assert_not_called()
        
        # Verify that the result is as expected
        assert result == {"status": "success"}


def test_track_with_event_object(mock_telemetree):
    """Test the track method with an Event object."""
    event = Event(
        event_type="custom_event",
        telegram_id=123456789,
        username="test_user",
        firstname="Test",
        lastname="User"
    )
    
    with patch.object(mock_telemetree, '_transform_telegram_webhook') as mock_transform:
        result = mock_telemetree.track(event)
        
        # Verify that _transform_telegram_webhook was NOT called
        mock_transform.assert_not_called()
        
        # Verify that the result is as expected
        assert result == {"status": "success"}
