import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Initialize all configuration variables to None ---
ELASTICSEARCH_HOST = None
ELASTICSEARCH_INDEX_NAME = None
ELASTICSEARCH_USERNAME = None
ELASTICSEARCH_PASSWORD = None
ELASTICSEARCH_API_ID = None
ELASTICSEARCH_API_KEY = None
GEMINI_API_KEY = None
EMBEDDING_MODEL = None

# --- Load and validate core settings from environment ---

# Core provider settings
VECTOR_STORE_PROVIDER = os.getenv("VECTOR_STORE_PROVIDER")
if VECTOR_STORE_PROVIDER is None:
    raise ValueError("VECTOR_STORE_PROVIDER environment variable not set.")

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER")
if EMBEDDING_PROVIDER is None:
    raise ValueError("EMBEDDING_PROVIDER environment variable not set.")

LLM_PROVIDER = os.getenv("LLM_PROVIDER")
if LLM_PROVIDER is None:
    raise ValueError("LLM_PROVIDER environment variable not set.")
    
# Log settings
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")
if LOG_FILE_PATH is None:
    raise ValueError("LOG_FILE_PATH environment variable not set.")

LOG_LEVEL = os.getenv("LOG_LEVEL")
if LOG_LEVEL is None:
    raise ValueError("LOG_LEVEL environment variable not set.")

# --- Load and validate provider-specific settings ---

# Elasticsearch settings
if VECTOR_STORE_PROVIDER == "elasticsearch":
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
    if ELASTICSEARCH_HOST is None:
        raise ValueError("ELASTICSEARCH_HOST environment variable not set for Elasticsearch provider.")
    
    ELASTICSEARCH_INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX_NAME")
    if ELASTICSEARCH_INDEX_NAME is None:
        raise ValueError("ELASTICSEARCH_INDEX_NAME environment variable not set for Elasticsearch provider.")

    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
    ELASTICSEARCH_API_ID = os.getenv("ELASTICSEARCH_API_ID")
    ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")

    has_api_key_auth = ELASTICSEARCH_API_ID is not None and ELASTICSEARCH_API_KEY is not None
    has_basic_auth = ELASTICSEARCH_USERNAME is not None and ELASTICSEARCH_PASSWORD is not None

    if not has_api_key_auth and not has_basic_auth:
        raise ValueError("Either ELASTICSEARCH_API_ID/ELASTICSEARCH_API_KEY or ELASTICSEARCH_USERNAME/ELASTICSEARCH_PASSWORD must be set for Elasticsearch provider.")

# Embedding model settings
if EMBEDDING_PROVIDER == "sentence_transformer":
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    if EMBEDDING_MODEL is None:
        raise ValueError("EMBEDDING_MODEL environment variable not set for sentence_transformer provider.")

# LLM Provider settings
if LLM_PROVIDER == "gemini":
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        raise ValueError("GEMINI_API_KEY environment variable not set for Gemini provider.")
