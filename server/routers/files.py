from fastapi import APIRouter, Depends, Response

from dropbase.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile
from server.auth.dependency import CheckUserPermissions
from server.controllers.files import (  # create_file,; rename_file,
    FileController,
    delete_file,
    get_all_files,
    update_file,
)

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP))],
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
    return update_file(function_name, req)


@router.delete("/")
def delete_file_req(req: DeleteFile, response: Response):
    return delete_file(req)


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name: str, page_name: str, response: Response):
    return get_all_files(app_name, page_name)
