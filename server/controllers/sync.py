import importlib
import os

from pydantic import BaseModel

from server.controllers.query import get_table_columns
from server.controllers.utils import handle_state_context_updates, validate_column_name
from server.requests.dropbase_router import DropbaseRouter

token = os.getenv("DROPBASE_TOKEN")


def sync_table_columns(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state: dict,
    router: DropbaseRouter,
):
    try:
        columns = get_table_columns(app_name, page_name, file, state)
        if not validate_column_name(columns):
            return "Invalid column names present in the table", 400

        # call dropbase server
        payload = {"table_id": table.get("id"), "columns": columns, "type": file.get("type")}
        resp = router.misc.sync_table_columns(payload)
        handle_state_context_updates(resp)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


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


def get_page_state_context(app_name: str, page_name: str):
    state_module_name = f"workspace.{app_name}.{page_name}.state"
    context_module_name = f"workspace.{app_name}.{page_name}.context"
    state_module = importlib.import_module(state_module_name)
    context_module = importlib.import_module(context_module_name)
    state_module = importlib.reload(state_module)
    context_module = importlib.reload(context_module)
    State = getattr(state_module, "State")
    Context = getattr(context_module, "Context")
    state = _dict_from_pydantic_model(State)
    context = _dict_from_pydantic_model(Context)
    return {"state": state, "context": context}


def _dict_from_pydantic_model(model):
    data = {}
    for name, field in model.__fields__.items():
        if isinstance(field.outer_type_, type) and issubclass(field.outer_type_, BaseModel):
            data[name] = _dict_from_pydantic_model(field.outer_type_)
        else:
            data[name] = field.default
    return data
