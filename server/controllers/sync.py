import importlib
from typing import List

from pydantic import BaseModel

from server.controllers.python_from_string import run_df_function
from server.controllers.query import get_table_sql, run_sql_query_from_string
from server.controllers.utils import get_state
from server.schemas.files import DataFile
from server.schemas.table import FilterSort


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


def _get_table_columns(app_name: str, page_name: str, file: DataFile, state: dict) -> List[str]:
    filter_sort = FilterSort(filters=[], sorts=[])

    if file.type == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state)
    else:
        sql = get_table_sql(app_name, page_name, file.name)
        df = run_sql_query_from_string(sql, file.source, app_name, page_name, state, filter_sort)
    return df.columns.tolist()
