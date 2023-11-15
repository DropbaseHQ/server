import json

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
from server.schemas.workspace import ConvertTableRequest, UpdateTableRequest
from server.worker.sync import get_table_columns
from server.requests.dropbase_router import DropbaseRouter, AccessCookies


def update_table(table_id: str, req: dict, access_cookies: AccessCookies):
    req: UpdateTableRequest = UpdateTableRequest(**req)
    update_table_payload = {
        "name": req.name,
        "table_id": req.table.get("id"),
        "file_id": req.file.get("id"),
        "page_id": req.page_id,
        "property": req.table.get("property"),
    }
    router = DropbaseRouter(cookies=access_cookies)
    # check if file has changed
    table_columns = []
    if req.file.get("id") == req.table.get("file_id"):
        resp = router.table.update_table(
            table_id=table_id, update_data=update_table_payload
        )

    else:
        if req.file.get("type") == "sql":
            sql = get_table_sql(req.app_name, req.page_name, req.file.get("name"))
            depends_on = get_sql_variables(user_sql=sql)
            update_table_payload["depends_on"] = depends_on
        table_columns = get_table_columns(
            req.app_name, req.page_name, req.table, req.file, req.state
        )
        update_table_payload["table_columns"] = table_columns
        resp = router.table.update_table_columns(
            table_id=table_id, update_data=update_table_payload
        )
    handle_state_context_updates(resp)
    return resp.json()


def convert_table(req: dict, access_cookies: AccessCookies):
    req = ConvertTableRequest(**req)
    router = DropbaseRouter(cookies=access_cookies)
    state = json.loads(req.state)
    state = get_state(req.app_name, req.page_name, state)
    file = DataFile(**req.file)
    # get db schema
    user_db_engine = connect_to_user_db(file.source)
    db_schema, gpt_schema = get_db_schema(user_db_engine)
    # get columns
    # TODO: get user sql from file
    user_sql = ""
    column_names = get_column_names(user_db_engine, user_sql)
    sql = render_sql(req.user_sql, state)

    # get columns from file
    get_smart_table_payload = {
        "db_schema": db_schema,
        "gpt_schema": gpt_schema,
        "column_names": column_names,
        "sql": sql,
    }
    resp = router.misc.get_smart_columns(**get_smart_table_payload)
    smart_cols = resp.get("columns")

    # validate columns
    validated = validate_smart_cols(user_db_engine, smart_cols, req.user_sql)
    smart_columns = {
        name: value for name, value in smart_cols.items() if name in validated
    }

    # get columns from file
    update_smart_cols_payload = {"smart_columns": smart_columns, "table": req.misc}
    resp = router.misc.update_smart_columns(**update_smart_cols_payload)
    return handle_state_context_updates(resp)
