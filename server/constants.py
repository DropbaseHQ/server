import os

from server.config import server_envs

cwd = os.getcwd()

HOST_PATH = server_envs.get("host_path")

CORS_ORIGINS = server_envs.get("cors_origins") or ["http://localhost:3030"]
REDIS_HOST = server_envs.get("redis_host") or "redis"
TASK_TIMEOUT = server_envs.get("task_timeout") or 300
HOST_MOUNTS = server_envs.get("host_mounts") or []
AUTO_REMOVE_CONTAINER = server_envs.get("auto_remove_container") or True

DEFAULT_RESPONSES = {404: {"description": "Not found"}}
INFER_TYPE_SAMPLE_SIZE = 50
WORKER_VERSION = "0.4.*"
SLACK_WEBHOOK_FEEDBACK = (
    "https://hooks.slack.com/services/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"
)
ONBOARDING_URL = "https://onboarding.dropbase.io"

# configure default llm provider and model
LLMS = server_envs.get("llm")
if LLMS:
    # get the first provider
    DEFAULT_PROVIDER = next(iter(LLMS))
    default_provider_models = {"openai": "gpt-4o", "anthropic": "claude-3-5-sonnet-20240620"}
    DEFAULT_MODEL = LLMS.get(DEFAULT_PROVIDER).get("model") or default_provider_models.get(
        DEFAULT_PROVIDER
    )
else:
    DEFAULT_PROVIDER = None
    DEFAULT_MODEL = None

DEFAULT_MAX_TOKENS = 4096
