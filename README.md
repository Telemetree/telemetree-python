![](https://tc-images-api.s3.eu-central-1.amazonaws.com/gif_cropped.gif)

# Telegram Mini App analytics SDK for Python

[![PyPi license](https://badgen.net/pypi/license/pip/)](https://pypi.org/project/pip/)
[![PyPI pyversions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://test.pypi.org/project/telemetree/0.1.1/)

The Telemetree Python SDK provides a convenient way to track and analyze Telegram events using the Telemetree service. With this SDK, you can easily capture and send Telegram events to the Telemetree platform for further analysis and insights.

![Alt](https://repobeats.axiom.co/api/embed/18ee5bb9c80b65e0e060cd5b16802b38262b2a87.svg "Repobeats analytics image")

### Features

- Automatically capture Telegram events and send them to Telemetree
- Encrypt event data using a hybrid approach with RSA and AES encryption
- Customize the events and commands to track
- Simple and intuitive API for easy integration

### Installation

You can install the Telemetree Python SDK using pip:

```shell
pip install telemetree
```

### Usage

1. Import the Telemetree SDK:

```python
from telemetree import TelemetreeClient
```

2. Initialize the client with your API key and project ID:

```python
api_key = "YOUR_API_KEY"
project_id = "YOUR_PROJECT_ID"

client = TelemetreeClient(api_key, project_id)
```

3. Connect the client to your webhook, or pass the event data directly:

```python
# Option 1: Pass raw Telegram webhook data directly
# The SDK will automatically detect and transform Telegram webhook data
webhook_data = {
    "update_id": 123456789,
    "message": {
        "message_id": 1,
        "from": {
            "id": 987654321,
            "is_bot": False,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "language_code": "en"
        },
        "chat": {
            "id": 987654321,
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "type": "private"
        },
        "date": 1621234567,
        "text": "Hello, world!"
    }
}

response_status_code = client.track(webhook_data)
print(response_status_code)

# Option 2: Pass a pre-formatted event
custom_event = {
    "event_type": "custom_event",
    "telegram_id": 987654321,
    "username": "johndoe",
    "firstname": "John",
    "lastname": "Doe"
}

response_status_code = client.track(custom_event)
print(response_status_code)
```

### Automatic Telegram Webhook Handling

The Telemetree SDK automatically detects and transforms Telegram webhook data into the required format. When you pass a raw Telegram webhook payload to the `track` method, the SDK will:

1. Detect that it's a Telegram webhook based on the presence of the `update_id` field and other Telegram-specific fields
2. Extract the user ID and other user information from the appropriate location in the webhook data
3. Transform the data into the format required by Telemetree
4. Track the event with the appropriate event type (e.g., `telegram_message`, `telegram_callback_query`, etc.)

This means you can directly pass the webhook data from your Telegram bot to Telemetree without any manual transformation:

```python
@app.route("/webhook", methods=["POST"])
async def telegram_webhook():
    data = await request.json()

    # Pass the raw webhook data directly to Telemetree
    telemetree_client.track(data)

    # Process the webhook data for your bot
    # ...

    return {"status": "ok"}
```

### Configuration

The Telemetree Python SDK provides some configuration options that you can customize:

- `auto_capture_telegram`: Enables or disables automatic capturing of Telegram events (default: `True`)
- `auto_capture_telegram_events`: Specifies the types of Telegram events to capture automatically (default: `["message"]`)
- `auto_capture_commands`: Specifies the Telegram commands to capture automatically (default: `["/start", "/help"]`)

Other configuration options include the Telemetree API endpoint, encryption keys, and logging settings. You can modify these options either within the Telemetree dashboard or by updating the `config.py` file in the SDK.

### Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

### License

This project is licensed under the MIT License. See the LICENSE file for more information.

### Support

If you have any questions or need assistance, please contact our support team at support@ton.solutions.
