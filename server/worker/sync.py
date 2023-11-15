import os
from typing import List
from server import requests as dropbase_router
from server.controllers.sync import _get_table_columns
from server.controllers.utils import handle_state_context_updates
from server.schemas.files import DataFile
from server.schemas.table import TableBase


token = os.getenv("DROPBASE_PROXY_SERVER_TOKEN")


def sync_table_columns(app_name: str, page_name: str, tables: List[dict], state):
    compiled_table_columns = {}
    for items in tables:
        table = TableBase(**items.get("table"))
        file = DataFile(**items.get("file"))
        table_columns = _get_table_columns(app_name, page_name, file, state=state)
        compiled_table_columns[table.id] = table_columns

    # call dropbase server
    payload = {
        "app_name": app_name,
        "page_name": page_name,
        "table_columns": compiled_table_columns,
        "table_type": file.type,
        "token": token,
    }
    resp = dropbase_router.sync_table_columns(**payload)
    return handle_state_context_updates(resp)


def get_table_columns(app_name: str, page_name: str, table: dict, file: dict, state):
    table = TableBase(**table)
    file = DataFile(**file)
    return _get_table_columns(app_name, page_name, file, state=state)


def sync_components(app_name: str, page_name: str):
    payload = {"app_name": app_name, "page_name": page_name, "token": token}
    resp = dropbase_router.sync_components(**payload)
    return handle_state_context_updates(resp)
