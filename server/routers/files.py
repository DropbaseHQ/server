from fastapi import APIRouter

from dropbase.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile, UpdateMainFile
from server.constants import DEFAULT_RESPONSES
from server.controllers.files import FileController, update_main_file

router = APIRouter(prefix="/files", tags=["files"], responses=DEFAULT_RESPONSES)


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


@router.get("/get_functions/{app_name}/{page_name}/")
def get_functions_req(app_name, page_name):
    file = FileController(app_name, page_name)
    return file.get_functions()


@router.put("/main/")
def update_main_files_req(req: UpdateMainFile):
    return update_main_file(req)
