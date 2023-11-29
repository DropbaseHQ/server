# TREVOR TODO migrate this
# from server.controllers.query import (
#     get_column_names,
#     get_sql_variables,
#     get_table_sql,
#     render_sql,
# )
from server.controllers.source import get_db_schema
from server.controllers.utils import (
    connect_to_user_db,
    get_state,
    handle_state_context_updates,
)
from server.controllers.validation import validate_smart_cols
from server.requests.dropbase_router import AccessCookies, DropbaseRouter
from server.schemas.files import DataFile


def convert_table(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state: dict,
    access_cookies: AccessCookies,
):
    try:
        state = get_state(app_name, page_name, state)
        file = DataFile(**file)
        # get db schema
        user_db_engine = connect_to_user_db(file.source)
        db_schema, gpt_schema = get_db_schema(user_db_engine)
        # get columns
        user_sql = get_table_sql(app_name, page_name, file.name)
        column_names = get_column_names(user_db_engine, user_sql)
        user_sql = render_sql(user_sql, state)
        router = DropbaseRouter(cookies=access_cookies)

        # get columns from file
        get_smart_table_payload = {
            "user_sql": user_sql,
            "column_names": column_names,
            "gpt_schema": gpt_schema,
            "db_schema": db_schema,
        }

        resp = router.misc.get_smart_columns(get_smart_table_payload)
        if resp.status_code != 200:
            return resp.text

        resp = resp.json()
        smart_cols = resp.get("columns")

        # validate columns
        validated = validate_smart_cols(user_db_engine, smart_cols, user_sql)
        smart_columns = {name: value for name, value in smart_cols.items() if name in validated}

        # get columns from file
        update_smart_cols_payload = {"smart_columns": smart_columns, "table": table}
        # print(update_smart_cols_payload)
        resp = router.misc.update_smart_columns(update_smart_cols_payload)
        handle_state_context_updates(resp)
        return resp.json(), 200
    except Exception as e:
        return str(e), 500
