from fastapi import APIRouter, Depends, HTTPException, Response

from server.auth.dependency import EnforceUserAppPermissions
from server.controllers.files import create_file, delete_file, get_all_files, rename_file, update_file
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(EnforceUserAppPermissions(action="edit"))],
)


@router.post("/")
def create_file_req(req: CreateFile, resp: Response):
    try:
        return create_file(req)
    except HTTPException as e:
        resp.status_code = e.status_code
        return {"message": str(e.detail)}
    except Exception as e:
        resp.status_code = 400
        return {"message": str(e)}


@router.put("/rename")
def rename_file_req(req: RenameFile, response: Response):
    try:
        return rename_file(req)
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}


@router.put("/{function_name}")
def update_file_req(function_name: str, req: UpdateFile, response: Response):
    try:
        return update_file(function_name, req)
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}


@router.delete("/")
def delete_file_req(req: DeleteFile, response: Response):
    try:
        delete_file(req)
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name: str, page_name: str, response: Response):
    try:
        return get_all_files(app_name, page_name)
    except Exception as e:
        response.status_code = 400
        return {"message": str(e)}
