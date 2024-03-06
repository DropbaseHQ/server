from typing import List

from dropbase.database.connect import connect
from dropbase.schemas.edit_cell import CellEdit
from dropbase.schemas.files import DataFile


def edit_cell(file: DataFile, edits: List[CellEdit]):
    result_dict = {"result": [], "errors": None}
    status_code = 200
    try:
        user_db = connect(file.source)
        for edit in edits:
            update_res, success = user_db._update_value(edit)
            result_dict["result"].append(update_res)
            if not success:
                status_code = 400
    except Exception as e:
        result_dict["errors"] = str(e)
        status_code = 500
    return result_dict, status_code
