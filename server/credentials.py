from server.settings import config

OPENAI_API_KEY = config.get("open_api_key")
OPENAI_ORG_ID = config.get("open_api_org_id")

# TODO: rename to WORKSPACE_HOST, WORKSPACE_PORT... or something similar. should not be postgres specific
POSTGRES_DB_HOST = config.get("postgres_db_host")
POSTGRES_DB_NAME = config.get("postgres_db_name")
POSTGRES_DB_USER = config.get("postgres_db_user")
POSTGRES_DB_PASS = config.get("postgres_db_pass")
POSTGRES_DB_PORT = config.get("postgres_db_port")
