from server.controllers.query import get_sql_variables, get_table_sql, render_sql, get_column_names, verify_state
from server.controllers.source import get_db_schema
from server.controllers.sync import get_table_columns
from server.controllers.utils import connect_to_user_db, validate_column_name, handle_state_context_updates
from server.controllers.validation import validate_smart_cols
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.files import DataFile
from server.schemas.workspace import UpdateTableRequest


def update_table(table_id: str, req: UpdateTableRequest, router: DropbaseRouter):
    update_table_payload = {
        "table_id": table_id,
        "page_id": req.page_id,
        "table_updates": req.table_updates.dict(),
    }
    try:
        # get depends on for sql files
        if req.file.get("type") == "sql":
            sql = get_table_sql(req.app_name, req.page_name, req.file.get("name"))
            depends_on = get_sql_variables(user_sql=sql)
            update_table_payload["depends_on"] = depends_on

        resp = router.table.update_table(table_id=table_id, update_data=update_table_payload)
        return resp.json(), resp.status_code
    except Exception as e:
        return str(e), 500


def update_table_columns(table_id: str, req: UpdateTableRequest, router: DropbaseRouter):
    try:
        columns = get_table_columns(req.app_name, req.page_name, req.file, req.state)
        if not validate_column_name(columns):
            return {"message": "Invalid column names present in the table"}, 400
        payload = {"table_id": table_id, "columns": columns, "type": req.file.get("type")}
        resp = router.sync.sync_columns(payload)
        return resp.json(), 200
    except Exception as e:
        return {"message": str(e)}, 500


def convert_table(
    app_name: str,
    page_name: str,
    table: dict,
    file: dict,
    state: dict,
    router: DropbaseRouter,
):
    try:
        resp, status_code = verify_state(app_name, page_name, state)
        if status_code != 200:
            raise Exception(resp["result"])

        file = DataFile(**file)
        # get db schema
        user_db_engine = connect_to_user_db(file.source)
        db_schema, gpt_schema = get_db_schema(user_db_engine)
        # get columns
        user_sql = get_table_sql(app_name, page_name, file.name)
        column_names = get_column_names(user_db_engine, user_sql)
        user_sql = render_sql(user_sql, state)

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
