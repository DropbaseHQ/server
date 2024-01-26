import os
import re

cwd = os.getcwd()


DROPBASE_TOKEN = os.getenv("DROPBASE_TOKEN")
DROPBASE_API_URL = os.getenv("DROPBASE_API_URL") or "https://api.dropbase.io"
TASK_TIMEOUT = os.getenv("TASK_TIMEOUT") or 60
STALE_TABLE_TIMEOUT = os.getenv("STALE_TABLE_TIMEOUT") or 6

# system constants
DF_TABLES_DB = "df_tables.db"
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50
FILE_NAME_REGEX = re.compile(r"^[A-Za-z0-9_.]+$")
WORKER_VERSION = "0.2.0"
