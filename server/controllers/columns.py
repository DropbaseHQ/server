from server.controllers.generate_models import create_state_context_files
from server.controllers.page import get_page_state_context
from server.controllers.utils import read_page_properties, validate_column_name, write_page_properties
from server.schemas.workspace import CommitTableColumnsRequest


def commit_table_columns(req: CommitTableColumnsRequest):
    # validate column
    for column in req.columns:
        if not validate_column_name(column.name):
            return {"message": "Invalid column names present in the table"}, 400

    # get properties
    properties = read_page_properties(req.app_name, req.page_name)
    # update columns
    for table in properties["tables"]:
        if table["name"] == req.table.name:
            table["columns"] = req.columns
            break
    # write properties
    write_page_properties(req.app_name, req.page_name, properties)

    # update state context
    create_state_context_files(properties)

    # get new steate and context
    return get_page_state_context(req.app_name, req.page_name)
