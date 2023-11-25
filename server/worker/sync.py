import os
from server.controllers.sync import _get_table_columns
from server.controllers.utils import handle_state_context_updates, validate_column_name
from server.schemas.files import DataFile
from server.schemas.table import TableBase
from server.requests.dropbase_router import DropbaseRouter, AccessCookies


token = os.getenv("DROPBASE_PROXY_SERVER_TOKEN")


def sync_table_columns(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state,
    access_cookies: AccessCookies,
):
    try:
        table = TableBase(**table)
        file = DataFile(**file)
        columns = _get_table_columns(app_name, page_name, file, state=state)
        if not validate_column_name(columns):
            return "Invalid column names present in the table", 400

        # call dropbase server
        payload = {"table_id": table.id, "columns": columns, "type": file.type}
        router = DropbaseRouter(cookies=access_cookies)
        resp = router.misc.sync_table_columns(payload)
        handle_state_context_updates(resp)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


def get_table_columns(app_name: str, page_name: str, table: dict, file: dict, state):
    table = TableBase(**table)
    file = DataFile(**file)
    return _get_table_columns(app_name, page_name, file, state=state)


def sync_components(app_name: str, page_name: str, router: DropbaseRouter):
    try:
        payload = {"app_name": app_name, "page_name": page_name, "token": token}
        resp = router.misc.sync_table_columns(**payload)
        handle_state_context_updates(resp)
        return resp.json(), 200
    except Exception as e:
        return {"error": str(e)}, 500


def sync_page(page_id: str, router: DropbaseRouter):
    resp = router.sync.sync_page(page_id=page_id)
    return handle_state_context_updates(resp)
