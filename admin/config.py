import os
from dotenv import load_dotenv

load_dotenv()

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
if LOG_FILE_PATH is None:
    raise ValueError("LOG_FILE_PATH environment variable not set.")

LOG_LEVEL = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    raise ValueError("LOG_LEVEL environment variable not set.")
