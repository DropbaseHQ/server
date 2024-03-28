import os

from server.controllers.sources import get_sources
from server.settings import config

cwd = os.getcwd()


DROPBASE_TOKEN = config.get("dropbase_token")
DROPBASE_API_URL = config.get("dropbase_api_url") or "https://api.dropbase.io"
CORS_ORIGINS = config.get("cors_origins") or ["http://localhost:3030", "http://www.localhost:3030"]
TASK_TIMEOUT = config.get("task_timeout") or 60
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50
WORKSPACE_SOURCES = get_sources()


WORKER_VERSION = "0.2.6"
REDIS_HOST = config.get("redis_host") or "host.docker.internal"

CUSTOM_PERMISSIONS_EXPIRY_TIME = config.get("permissions_expiry_time") or 60
