import logging
from logging.handlers import RotatingFileHandler

from app.config.setting import get_settings

settings = get_settings()
# Configure logger
logger = logging.getLogger(settings.lOGGER_NAME)
logger.setLevel(logging.INFO)

# Create a file handler for logging
file_handler = RotatingFileHandler(
    f'{settings.lOGGER_NAME}.log',          # Log file name
    maxBytes=10**6,     # Maximum file size in bytes (1 MB)
    backupCount=5       # Number of backup files to keep
)
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the file handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)
