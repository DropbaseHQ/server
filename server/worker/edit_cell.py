from typing import List

from server.controllers.edit_cell import update_value
from server.controllers.utils import connect_to_user_db
from server.schemas.edit_cell import CellEdit


def edit_cell(file: dict, edits: List[CellEdit]):
    result_dict = {"result": [], "errors": None}
    try:
        user_db_engine = connect_to_user_db(file.get("source"))
        for edit in edits:
            update_res = update_value(user_db_engine, edit)
            result_dict["result"].append(update_res)
        user_db_engine.dispose()
        status_code = 200
    except Exception as e:
        result_dict["errors"] = str(e)
        status_code = 500
    return result_dict, status_code
