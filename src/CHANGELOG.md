## 0.4.0 (2025-04-21)

### Feat

- **client.py**: Added automatic Telegram webhook detection and transformation
  - The SDK now automatically detects when a raw Telegram webhook payload is passed to the `track` method
  - Automatically extracts user information and transforms the data into the required Telemetree format
  - Supports all Telegram update types (messages, callback queries, inline queries, etc.)
  - Improves developer experience by eliminating the need for manual data transformation

## 0.3.0 (2025-03-05)

### Feat

- **revamped-python-library**: we re-wroted the python library -- made it easy to use it with backend services

## 0.2.0 (2024-07-10)

### Feat

- **client.py,-config.py,-orchestrator.py**: new event transformation orchestrator

### Fix

- **config.py**: added tracked_messages and app_name

### Refactor

- **telemetree-folder**: fixed imports

## 0.1.6 (2024-03-12)

### Fix

- **init.py**: improved telemetreeclient import

## 0.1.5 (2024-03-12)

### Fix

- **setuptools**: Fixed the build error

## 0.1.4 (2024-03-12)

### Fix

- **pycryptodome**: fixed library import

## 0.1.3 (2024-03-12)

### Fix

- **reqs**: add setuptools

## 0.1.2 (2024-03-12)

### Fix

- **telemetree**: fixed dependencies

## 0.1.1 (2024-03-11)

### Fix

- **setup.py**: Prepared for the test PyPI deploy

## 0.1.0 (2024-03-05)

### Feat

- **tests**: implemented the test suite for encryption and event builder
