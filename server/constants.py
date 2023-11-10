import os

from dotenv import load_dotenv

load_dotenv()
cwd = os.getcwd()


DROPBASE_API_URL = (
    os.getenv("DROPBASE_API_URL") if os.getenv("DROPBASE_API_URL") else "https://api.dropbase.io"
)
