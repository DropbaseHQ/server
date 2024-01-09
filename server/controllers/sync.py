from server.constants import DROPBASE_TOKEN
from server.controllers.query import get_table_columns
from server.controllers.utils import handle_state_context_updates, validate_column_name
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.sync import SyncTableColumns


def sync_table_columns(req: SyncTableColumns, router: DropbaseRouter):
    try:
        # import pdb
        # pdb.set_trace()
        columns = get_table_columns(req.app_name, req.page_name, req.file, req.state)
        if not validate_column_name(columns):
            return "Invalid column names present in the table", 400

        # call dropbase server
        payload = {"table_id": req.table.get("id"), "columns": columns, "type": req.file.get("type")}
        resp = router.misc.sync_table_columns(payload)
        # print(resp.json())
        # import pdb; pdb.set_trace()
        handle_state_context_updates(resp)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


def sync_components(app_name: str, page_name: str, router: DropbaseRouter):
    try:
        payload = {"app_name": app_name, "page_name": page_name, "token": DROPBASE_TOKEN}
        resp = router.misc.sync_components(**payload)
        handle_state_context_updates(resp)
        return resp.json(), 200
    except Exception as e:
        return {"error": str(e)}, 500
