import os

from server.controllers.sources import get_sources
from server.settings import config

cwd = os.getcwd()

GPT_MODEL = "gpt-3.5-turbo"
GPT_TEMPERATURE = 0.0

CORS_ORIGINS = config.get("cors_origins") or [config.get("client_url")]
TASK_TIMEOUT = config.get("task_timeout") or 60
INFER_TYPE_SAMPLE_SIZE = 50
WORKSPACE_SOURCES = get_sources()


WORKER_VERSION = "0.4.0"
REDIS_HOST = config.get("redis_host") or "host.docker.internal"
