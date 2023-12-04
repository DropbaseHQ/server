import os
import re

cwd = os.getcwd()


DROPBASE_TOKEN = os.getenv("DROPBASE_TOKEN")
DROPBASE_API_URL = (
    os.getenv("DROPBASE_API_URL") if os.getenv("DROPBASE_API_URL") else "https://api.dropbase.io"
)
DATA_PREVIEW_SIZE = 100
FILE_NAME_REGEX = re.compile(r"^[A-Za-z0-9_.]+$")
WORKER_VERSION = "0.0.3"
