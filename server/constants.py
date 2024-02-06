import os
import re

from server.controllers.sources import get_sources

cwd = os.getcwd()


DROPBASE_TOKEN = os.getenv("DROPBASE_TOKEN")
DROPBASE_API_URL = os.getenv("DROPBASE_API_URL") or "https://api.dropbase.io"
TASK_TIMEOUT = os.getenv("TASK_TIMEOUT") if os.getenv("TASK_TIMEOUT") else 60
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50

FILE_NAME_REGEX = re.compile(r"^[A-Za-z0-9_.]+$")
WORKER_VERSION = "0.2.0"

WORKSPACE_ID = os.getenv("WORKSPACE_ID")

WORKSPACE_SOURCES = get_sources()
