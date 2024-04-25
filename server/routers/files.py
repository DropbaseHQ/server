from fastapi import APIRouter

from dropbase.schemas.files import UpdateFile
from server.controllers.files import FileController
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
    dependencies=get_permission_dependency_array(action="edit", resource="app"),
)


@router.put("/{function_name}")
def update_file_req(function_name: str, req: UpdateFile):
    file = FileController(req.app_name, req.page_name)
    return file.update_file(req)


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name: str, page_name: str):
    file = FileController(app_name, page_name)
    return file.get_all_files()


@router.get("/get_functions/{app_name}/{page_name}/")
def get_functions_req(app_name, page_name):
    file = FileController(app_name, page_name)
    return file.get_functions()
