from server.settings import config

CLIENT_URL = config.get("client_url") or "http://localhost:3030"

GPT_MODEL = "gpt-3.5-turbo"
GPT_TEMPERATURE = 0.0


ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 1  # 1 day
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

# Ordered from most to least privileged
ALLOWED_ACTIONS = ["own", "edit", "use"]
WORKSPACE_ID = "00000000-0000-0000-0000-000000000000"
