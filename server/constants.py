import os

from server.config import server_envs

cwd = os.getcwd()

HOST_PATH = server_envs.get("host_path")

CORS_ORIGINS = server_envs.get("cors_origins") or ["http://localhost:3030"]
REDIS_HOST = server_envs.get("redis_host") or "redis"
TASK_TIMEOUT = server_envs.get("task_timeout") or 300
HOST_MOUNTS = server_envs.get("host_mounts") or []

DEFAULT_RESPONSES = {404: {"description": "Not found"}}
INFER_TYPE_SAMPLE_SIZE = 50
WORKER_VERSION = "0.4.*"
SLACK_WEBHOOK_FEEDBACK = (
    "https://hooks.slack.com/services/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"
)
ONBOARDING_URL = "https://onboarding.dropbase.io"
