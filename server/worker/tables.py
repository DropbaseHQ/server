from server import requests as dropbase_router
from server.controllers.query import (
    get_column_names,
    get_sql_variables,
    get_table_sql,
    render_sql,
)
from server.controllers.source import get_db_schema
from server.controllers.utils import (
    connect_to_user_db,
    get_state,
    handle_state_context_updates,
)
from server.controllers.validation import validate_smart_cols
from server.schemas.files import DataFile
from server.schemas.workspace import UpdateTableRequest
from server.worker.sync import get_table_columns
from server.requests.dropbase_router import DropbaseRouter, AccessCookies


def update_table(table_id: str, req: UpdateTableRequest, access_cookies: AccessCookies):
    update_table_payload = {
        "name": req.name,
        "table_id": req.table.get("id"),
        "file_id": req.file.get("id"),
        "page_id": req.page_id,
        "property": req.table.get("property"),
    }
    router = DropbaseRouter(cookies=access_cookies)
    # get depends on for sql files
    if req.file.get("type") == "sql":
        sql = get_table_sql(req.app_name, req.page_name, req.file.get("name"))
        depends_on = get_sql_variables(user_sql=sql)
        update_table_payload["depends_on"] = depends_on

    return router.table.update_table(
        table_id=table_id, update_data=update_table_payload
    )


def update_table_columns(table_id: str, req: UpdateTableRequest):
    try:
        columns = get_table_columns(
            req.app_name, req.page_name, req.table, req.file, req.state
        )
        payload = {
            "table_id": table_id,
            "columns": columns,
            "type": req.file.get("type"),
        }
        resp = dropbase_router.sync_columns(payload)
        handle_state_context_updates(resp)
        return "Columns updated successfully"
    except Exception as e:
        print(e)
        return "Failed to update table columns"


def convert_table(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state: dict,
    access_cookies: AccessCookies,
):
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
    smart_columns = {
        name: value for name, value in smart_cols.items() if name in validated
    }

    # get columns from file
    update_smart_cols_payload = {"smart_columns": smart_columns, "table": table}
    # print(update_smart_cols_payload)
    resp = router.misc.update_smart_columns(update_smart_cols_payload)
    return handle_state_context_updates(resp)
