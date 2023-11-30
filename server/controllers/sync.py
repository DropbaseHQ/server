import importlib
from typing import List

from pydantic import BaseModel

from server.controllers.python_from_string import run_df_function
from server.controllers.query import get_table_sql, run_df_query
from server.controllers.utils import get_state
from server.schemas.files import DataFile
from server.schemas.table import FilterSort


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


def _get_table_columns(app_name: str, page_name: str, file: DataFile, state) -> List[str]:
    filter_sort = FilterSort(filters=[], sorts=[])
    state = get_state(app_name, page_name, state)

    if file.type == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state)
    else:
        sql = get_table_sql(app_name, page_name, file.name)
        df = run_df_query(sql, file.source, state, filter_sort)
    return df.columns.tolist()
