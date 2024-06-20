from fastapi import APIRouter, HTTPException

from dropbase.schemas.files import UpdateFile
from server.constants import DEFAULT_RESPONSES
from server.controllers.files import update_main_file

router = APIRouter(prefix="/files", tags=["files"], responses=DEFAULT_RESPONSES)


@router.put("/")
def update_main_files_req(req: UpdateFile):
    try:
        return update_main_file(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
