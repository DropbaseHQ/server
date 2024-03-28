from dropbase.schemas.table import CommitTableColumnsRequest
from server.controllers.page import get_page_state_context
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.utils import validate_column_name


def commit_table_columns(req: CommitTableColumnsRequest):
    # validate column
    for column in req.columns:
        if not validate_column_name(column.name):
            return {"message": "Invalid column names present in the table"}, 400

    # get properties
    properties = read_page_properties(req.app_name, req.page_name)
    # update columns
    for block in properties["blocks"]:
        if block["name"] == req.table.name and block["block_type"] == "table":
            block["columns"] = req.columns
            break

    update_properties(req.app_name, req.page_name, properties)

    # get new steate and context
    return get_page_state_context(req.app_name, req.page_name)
