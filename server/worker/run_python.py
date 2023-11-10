from server.controllers.utils import (
    call_function,
    clean_df,
    get_data_function_by_file,
    get_function_by_name,
    get_state,
    get_state_context,
)
from server.schemas.files import DataFile
from server.schemas.table import FilterSort


def run_python_query(app_name, page_name, file: DataFile, state: dict, filter_sort: FilterSort):
    state = get_state(app_name, page_name, state)
    args = {"state": state, "filter_sort": filter_sort}
    function_name = get_data_function_by_file(app_name, page_name, file)
    df = call_function(function_name, **args)
    df = clean_df(df)
    return {"columns": df.columns.tolist(), "data": df.values.tolist()}


def run_python_ui(app_name: str, page_name: str, function_name: str, payload: dict):
    state, context = get_state_context(app_name, page_name, payload.get("state"), payload.get("context"))
    args = {"state": state, "context": context}
    function_name = get_function_by_name(app_name, page_name, function_name)
    context = function_name(**args)
    return {"context": context.dict()}
