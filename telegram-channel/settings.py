import os
import logging

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
STORAGE_ID = int(os.environ['STORAGE_ID'])
TELEGRAM_SESSION = os.environ['TELEGRAM_SESSION']
LOGGING_LEVEL = getattr(logging, os.environ.get('LOGGING_LEVEL', 'WARNING'))

del os
