import os
from server import requests as dropbase_router
from server.controllers.sync import _get_table_columns
from server.controllers.utils import handle_state_context_updates
from server.schemas.files import DataFile
from server.schemas.table import TableBase


token = os.getenv("DROPBASE_PROXY_SERVER_TOKEN")


def sync_table_columns(app_name: str, page_name: str, table: dict, file: dict, state):
    table = TableBase(**table)
    file = DataFile(**file)
    columns = _get_table_columns(app_name, page_name, file, state=state)

    # call dropbase server
    payload = {
        "table_id": table.id,
        "columns": columns,
        "type": file.type
    }
    resp = dropbase_router.sync_columns(payload)
    return handle_state_context_updates(resp)


def get_table_columns(app_name: str, page_name: str, table: dict, file: dict, state):
    table = TableBase(**table)
    file = DataFile(**file)
    return _get_table_columns(app_name, page_name, file, state=state)


def sync_components(app_name: str, page_name: str):
    payload = {"app_name": app_name, "page_name": page_name, "token": token}
    resp = dropbase_router.sync_components(**payload)
    return handle_state_context_updates(resp)


def sync_page(page_id: str):
    resp = dropbase_router.sync_page(page_id=page_id)
    return handle_state_context_updates(resp)
