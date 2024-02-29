import os

from dotenv import load_dotenv

from dropbase.database.sources import get_sources

load_dotenv()

cwd = os.getcwd()


DROPBASE_TOKEN = os.environ.get("DROPBASE_TOKEN")
DROPBASE_API_URL = os.environ.get("DROPBASE_API_URL") or "https://api.dropbase.io"
CORS_ORIGINS = os.environ.get("CORS_ORIGINS") or '["http://localhost:3030", "http://www.localhost:3030"]'
TASK_TIMEOUT = os.environ.get("TASK_TIMEOUT") or 60
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50
WORKSPACE_SOURCES = get_sources()


WORKER_VERSION = "0.2.6"
REDIS_HOST = os.environ.get("REDIS_HOST") or "host.docker.internal"

CUSTOM_PERMISSIONS_EXPIRY_TIME = os.environ.get("PERMISSIONS_EXPIRY_TIME") or 60
