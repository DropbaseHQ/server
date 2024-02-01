from server.controllers.dataframe import convert_df_to_resp_obj
from server.controllers.utils import clean_df, get_function_by_name, get_state, get_state_context


def run_python_query(app_name: str, page_name: str, file: dict, state: dict):
    try:
        state = get_state(app_name, page_name, state)
        args = {"state": state}
        function_name = get_function_by_name(app_name, page_name, file.get("name"))
        # call function
        df = function_name(**args)
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
        # call function
        context = function_name(**args)
        return {"context": context.dict()}, 200
    except Exception as e:
        return {"error": str(e)}, 500
