import glob
import importlib
import os
from uuid import UUID
from fastapi import APIRouter, Response
from server import requests as dropbase_router
from server.constants import cwd
from server.controllers.files import (
    create_file,
    get_function_by_return_type,
    get_signature_models,
)
from server.controllers.utils import find_functions_by_signature, rename_function_in_file
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile

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
async def create_file_req(req: CreateFile, resp: Response):
    status_code, resonse = create_file(req)
    resp.status_code = status_code
    return resonse


@router.put("/rename")
async def rename_file(req: RenameFile):
    try:
        file_ext = ".sql" if req.type == "sql" else ".py"
        file_name = req.old_name + file_ext
        file_path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        )
        new_file_name = req.new_name + file_ext
        new_path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{new_file_name}"
        )
        if os.path.exists(file_path):
            os.rename(file_path, new_path)
        rename_function_in_file(
            file_path=new_path,
            old_name=req.old_name,
            new_name=req.new_name,
        )
        dropbase_router.update_file_name(
            update_data={
                "page_id": req.page_id,
                "old_name": req.old_name,
                "new_name": req.new_name,
            }
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/{file_id}")
async def update_file_req(file_id: UUID, req: UpdateFile):
    try:
        file_name = req.name + ".sql" if req.type == "sql" else req.name + ".py"
        file_path = (
            cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        )
        with open(file_path, "w") as f:
            f.write(req.sql)

        payload = {"name": req.name, "source": req.source}
        resp = dropbase_router.update_file(file_id=file_id, update_data=payload)
        return resp.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/{file_id}/")
def delete_file_req(file_id: str, req: DeleteFile, resp: Response):
    resp = dropbase_router.delete_file(file_id=file_id)
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


@router.get("/functions/{app_name}/{page_name}/{return_type}/")
async def get_function_files(app_name, page_name, return_type):
    try:
        # find which class to look for based on return type
        req_param_models, opt_param_models, return_model = get_signature_models(
            app_name, page_name, return_type
        )

        # get and filter out files
        dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
        module_path = f"workspace.{app_name}.{page_name}.scripts"

        table_functions = []
        python_files = glob.glob(f"{dir_path}/*.py")

        for py_file in python_files:
            if os.path.isfile(py_file) and not py_file.endswith("__init__.py"):
                script_name = os.path.splitext(os.path.basename(py_file))[0]
                module = importlib.import_module(module_path + "." + script_name)
                pandas_functions = find_functions_by_signature(
                    module,
                    req_param_types=req_param_models,
                    opt_param_types=opt_param_models,
                    return_type=return_model,
                )
                table_functions.extend(pandas_functions)
        return {"files": table_functions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/sql/{app_name}/{page_name}/")
async def get_sql_files(app_name, page_name):
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": sql_files}


@router.get("/python/{app_name}/{page_name}/")
async def get_python_files(app_name, page_name):
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    sql_files = glob.glob(os.path.join(dir_path, "*.py"))
    return {"files": [file for file in sql_files if not file.endswith("__init__.py")]}


@router.get("/all/{app_name}/{page_name}/")
async def get_all_files(app_name, page_name):
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    py_files = glob.glob(os.path.join(dir_path, "*.py"))
    py_files = [file for file in py_files if not file.endswith("__init__.py")]
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": py_files + sql_files}


@router.get("/table_options/{app_name}/{page_name}/")
async def get_table_options(app_name, page_name):
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    sqls = [sql[len(dir_path) + 1 :] for sql in sql_files]
    function = get_function_by_return_type(app_name, page_name, "pandas")
    return {"sql": sqls, "python": function}
