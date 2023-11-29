import os

from server.controllers.sync import _get_table_columns
from server.controllers.utils import handle_state_context_updates
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.files import DataFile
from server.schemas.table import TableBase

token = os.getenv("DROPBASE_TOKEN")


# TREVOR TODO move this out of worker
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
