from fastapi import APIRouter, Depends

from dropbase.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile
from server.controllers.files import FileController
from server.utils import get_permission_dependency_array

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
    dependencies=get_permission_dependency_array(action="edit", resource="app"),
)


@router.post("/")
def create_file_req(req: CreateFile):
    file = FileController(req.app_name, req.page_name)
    return file.create_file(req)


@router.put("/rename")
def rename_file_req(req: RenameFile):
    file = FileController(req.app_name, req.page_name)
    return file.rename_file(req)


@router.put("/{function_name}")
def update_file_req(function_name: str, req: UpdateFile):
    file = FileController(req.app_name, req.page_name)
    return file.update_file(req)


@router.delete("/")
def delete_file_req(req: DeleteFile):
    file = FileController(req.app_name, req.page_name)
    return file.delete_file(req)


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name: str, page_name: str):
    file = FileController(app_name, page_name)
    return file.get_all_files()
