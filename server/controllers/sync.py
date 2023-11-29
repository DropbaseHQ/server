import importlib
from typing import List

from pydantic import BaseModel

from server.controllers.python_from_string import run_df_function
from server.controllers.query import get_table_sql, run_sql_query_from_string
from server.controllers.utils import validate_column_name, handle_state_context_updates
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.files import DataFile
from server.schemas.table import TableBase, FilterSort


def sync_table_columns(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state,
    router: DropbaseRouter
):
    try:
        table = TableBase(**table)
        columns = get_table_columns(app_name, page_name, file, state=state)
        if not validate_column_name(columns):
            return "Invalid column names present in the table", 400

        # call dropbase server
        payload = {"table_id": table.id, "columns": columns, "type": file.get("type")}
        resp = router.misc.sync_table_columns(payload)
        handle_state_context_updates(resp)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


def get_page_state_context(app_name: str, page_name: str):
    module_name = f"workspace.{app_name}.{page_name}"
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    State = getattr(module, "State")
    Context = getattr(module, "Context")
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


def get_table_columns(app_name: str, page_name: str, file: dict, state: dict) -> List[str]:
    file = DataFile(**file)
    filter_sort = FilterSort(filters=[], sorts=[])

    if file.type == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state)
        columns = df.columns.tolist()
    else:
        sql = get_table_sql(app_name, page_name, file.name)
        resp, _ = run_sql_query_from_string(sql, file.source, app_name, page_name, state, filter_sort)
        columns = resp["result"]["columns"]
    return columns
