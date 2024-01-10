from server.controllers.dataframe import convert_df_to_resp_obj
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


def run_python_query(app_name, page_name, file: dict, state: dict, filter_sort: FilterSort):
    try:
        state = get_state(app_name, page_name, state)
        args = {"state": state, "filter_sort": filter_sort}
        file = DataFile(**file)
        function_name = get_data_function_by_file(app_name, page_name, file)
        df = call_function(function_name, **args)
        df = clean_df(df)
        return convert_df_to_resp_obj(df), 200
    except Exception as e:
        return {"error": str(e)}, 500


def run_python_ui(app_name: str, page_name: str, function_name: str, payload: dict):
    try:
        state, context = get_state_context(
            app_name, page_name, payload.get("state"), payload.get("context")
        )
        args = {"state": state, "context": context}
        function_name = get_function_by_name(app_name, page_name, function_name)
        context = function_name(**args)
        return {"context": context.dict()}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def run_df_function(app_name: str, page_name: str, file: dict, state: dict):
    try:
        file = DataFile(**file)
        state = get_state(app_name, page_name, state)
        function_name = get_data_function_by_file(app_name, page_name, file)
        df = function_name(state)
        df = clean_df(df)
        return df, 200
    except Exception as e:
        return {"error": str(e)}, 500
