import os

cwd = os.getcwd()


DROPBASE_API_URL = (
    os.getenv("DROPBASE_API_URL") if os.getenv("DROPBASE_API_URL") else "https://api.dropbase.io"
)
