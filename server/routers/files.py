import glob
import os
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from server.constants import FILE_NAME_REGEX, cwd
from server.controllers.files import create_file
from server.controllers.query import get_sql_variables
from server.controllers.utils import rename_function_in_file
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile

router = APIRouter(
    prefix="/files", tags=["files"], responses={404: {"description": "Not found"}}
)


@router.post("/")
def create_file_req(
    req: CreateFile,
    resp: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    status_code, resonse = create_file(req, router)
    resp.status_code = status_code
    return resonse


@router.put("/rename")
def rename_file_req(
    req: RenameFile, router: DropbaseRouter = Depends(get_dropbase_router)
):
    try:
        resp = router.file.update_file_name(
            update_data={
                "page_id": req.page_id,
                "old_name": req.old_name,
                "new_name": req.new_name,
            }
        )
        if resp.status_code == 200:
            file_ext = ".sql" if req.type == "sql" else ".py"
            file_name = req.old_name + file_ext
            file_path = (
                cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
            )
            new_file_name = req.new_name + file_ext
            new_path = (
                cwd
                + f"/workspace/{req.app_name}/{req.page_name}/scripts/{new_file_name}"
            )
            if os.path.exists(file_path):
                os.rename(file_path, new_path)
            rename_function_in_file(
                file_path=new_path,
                old_name=req.old_name,
                new_name=req.new_name,
            )
            return {"status": "success"}
        else:
            return {"status": "error", "message": resp.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/{file_id}")
def update_file_req(
    file_id: UUID,
    req: UpdateFile,
    response: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    try:
        file_extension = ".sql" if req.type == "sql" else ".py"
        file_name = req.name
        if not req.name.endswith(file_extension):
            file_name = req.name + file_extension

        file_path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        )
        with open(file_path, "w") as f:
            f.write(req.sql)

        if req.type != "sql" and req.name.endswith(".py"):
            stripped_file_name = req.name[:-3]
        else:
            stripped_file_name = req.name
        payload = {
            "file_id": str(file_id),
            "name": stripped_file_name,
            "source": req.source,
            "depends_on": [],
        }
        if req.type == "sql":
            depends_on = get_sql_variables(user_sql=req.sql)
            payload["depends_on"] = depends_on

        resp = router.file.update_file(file_id=file_id, update_data=payload)
        return resp.json()
    except Exception as e:
        response.status_code = 500
        return {"message": str(e)}


@router.delete("/{file_id}/")
def delete_file_req(
    file_id: str,
    req: DeleteFile,
    resp: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    resp = router.file.delete_file(file_id=file_id)
    if resp.status_code == 200:
        path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{req.file_name}"
        )
        if os.path.exists(path):
            os.remove(path)
        else:
            resp.status_code = 400
            return {"status": "error", "message": "The file does not exist"}
    else:
        resp.status_code = 400

    return resp.json()


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name, page_name):
    if not (
        re.match(FILE_NAME_REGEX, app_name) and re.match(FILE_NAME_REGEX, page_name)
    ):
        raise HTTPException(
            400,
            detail="app_name and file_name must be only use alphanumerics or underscores.",
        )
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    py_files = glob.glob(os.path.join(dir_path, "*.py"))
    py_files = [file for file in py_files if not file.endswith("__init__.py")]
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": py_files + sql_files}
