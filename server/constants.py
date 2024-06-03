import os

from server.config import server_envs

cwd = os.getcwd()

CORS_ORIGINS = server_envs.get("cors_origins") or [server_envs.get("client_url")]
INFER_TYPE_SAMPLE_SIZE = 50
WORKER_VERSION = "0.4.0"
REDIS_HOST = server_envs.get("redis_host") or "host.docker.internal"
DEFAULT_RESPONSES = {404: {"description": "Not found"}}
