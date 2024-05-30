from fastapi import APIRouter, HTTPException

from dropbase.schemas.files import UpdateFile
from server.constants import DEFAULT_RESPONSES
from server.controllers.files import FileController, update_main_file

router = APIRouter(prefix="/files", tags=["files"], responses=DEFAULT_RESPONSES)


@router.put("/")
def update_main_files_req(req: UpdateFile):
    try:
        return update_main_file(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_functions/{app_name}/{page_name}/")
def get_functions_req(app_name, page_name):
    file = FileController(app_name, page_name)
    return file.get_functions()
