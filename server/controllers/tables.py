from server.controllers.query import get_sql_variables, get_table_sql
from server.controllers.sync import get_table_columns
from server.controllers.utils import validate_column_name
from server.requests.dropbase_router import DropbaseRouter
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
