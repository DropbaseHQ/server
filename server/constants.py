import os

from dotenv import load_dotenv

from dropbase.database.sources import get_sources

load_dotenv()

cwd = os.getcwd()


DROPBASE_TOKEN = os.environ.get("DROPBASE_TOKEN")
DROPBASE_API_URL = os.environ.get("DROPBASE_API_URL") or "https://api.dropbase.io"
TASK_TIMEOUT = os.environ.get("TASK_TIMEOUT") or 60
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50
WORKSPACE_SOURCES = get_sources()


WORKER_VERSION = "0.2.3"
WORKER_IMAGE_VERSION = "0.0.2"
DOCKER_ENV = False
