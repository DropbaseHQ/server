import os

from server.config import config

cwd = os.getcwd()

CORS_ORIGINS = config.get("cors_origins") or [config.get("client_url")]
INFER_TYPE_SAMPLE_SIZE = 50
WORKER_VERSION = "0.4.0"
REDIS_HOST = config.get("redis_host") or "host.docker.internal"
DEFAULT_RESPONSES = {404: {"description": "Not found"}}
