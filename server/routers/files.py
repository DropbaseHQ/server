import glob
import os
from uuid import UUID

from fastapi import APIRouter, Response, Depends

from server.constants import cwd
from server.controllers.files import create_file
from server.controllers.utils import rename_function_in_file
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/files", tags=["files"], responses={404: {"description": "Not found"}}
)


@router.get("/read/{path}/")
async def read_file(path: str):
    try:
        with open(path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/")
async def create_file_req(
    req: CreateFile,
    resp: Response,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    status_code, resonse = create_file(req, router)
    resp.status_code = status_code
    return resonse


@router.put("/rename")
async def rename_file(
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
async def update_file_req(
    file_id: UUID,
    req: UpdateFile,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    try:
        file_name = req.name + ".sql" if req.type == "sql" else req.name + ".py"
        file_path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        )
        with open(file_path, "w") as f:
            f.write(req.sql)

        payload = {"name": req.name, "source": req.source}
        resp = router.file.update_file(file_id=file_id, update_data=payload)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/{file_id}/")
def delete_file_req(file_id: str, req: DeleteFile, resp: Response):
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
async def get_all_files(app_name, page_name):
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    py_files = glob.glob(os.path.join(dir_path, "*.py"))
    py_files = [file for file in py_files if not file.endswith("__init__.py")]
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": py_files + sql_files}
