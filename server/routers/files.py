import glob
import os
import re

from fastapi import APIRouter, HTTPException, Response

from server.constants import FILE_NAME_REGEX, cwd
from server.controllers.files import create_file
from server.controllers.query import get_sql_variables
from server.controllers.utils import read_page_properties, rename_function_in_file, write_page_properties
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile

router = APIRouter(prefix="/files", tags=["files"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_file_req(req: CreateFile, resp: Response):
    status_code, resonse = create_file(req)
    resp.status_code = status_code
    return resonse


@router.put("/rename")
def rename_file_req(req: RenameFile, response: Response):
    file_ext = ".sql" if req.type == "sql" else ".py"
    file_name = req.old_name + file_ext
    file_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"

    # if file does not exist, exit
    if not os.path.exists(file_path):
        response.status_code = 400
        return {"status": "error", "message": "The file does not exist"}

    try:
        new_file_name = req.new_name + file_ext
        new_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{new_file_name}"
        if os.path.exists(file_path):
            os.rename(file_path, new_path)
        rename_function_in_file(file_path=new_path, old_name=req.old_name, new_name=req.new_name)

        # update properties.json
        properties = read_page_properties(req.app_name, req.page_name)

        for file in properties["files"]:
            if file["name"] == req.old_name:
                file["name"] = req.new_name
                break

        write_page_properties(req.app_name, req.page_name, properties)

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/{function_name}")
def update_file_req(req: UpdateFile, function_name: str, response: Response):
    try:
        file_extension = ".sql" if req.type == "sql" else ".py"
        file_name = function_name + file_extension

        # update file content
        file_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        with open(file_path, "w") as f:
            f.write(req.sql)

        # update properties.json
        properties = read_page_properties(req.app_name, req.page_name)

        depends_on = []
        if req.type == "sql":
            # update depends on flags in properties.json
            depends_on = get_sql_variables(user_sql=req.sql)

            # for table in properties["tables"]:
            #     if table.get("fetcher") == function_name:
            #         table["depends_on"] = depends_on

        # update file property in properties.json
        for file in properties["files"]:
            if file["name"] == req.name:
                file["source"] = req.source
                file["type"] = req.type
                file["depends_on"] = depends_on
                break

        write_page_properties(req.app_name, req.page_name, properties)

        return {"status": "success"}
    except Exception as e:
        response.status_code = 500
        return {"message": str(e)}


@router.delete("/")
def delete_file_req(req: DeleteFile, response: Response):
    function_name = req.file_name[:-4] if req.type == "sql" else req.file_name[:-3]
    try:
        path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{req.file_name}"
        if not os.path.exists(path):
            response.status_code = 400
            return {"status": "error", "message": "The file does not exist"}

        os.remove(path)

        properties = read_page_properties(req.app_name, req.page_name)

        for file in properties["files"]:
            if file["name"] == function_name:
                properties["files"].remove(file)
                break

        write_page_properties(req.app_name, req.page_name, properties)

        return {"status": "success"}
    except Exception as e:
        response.status_code = 400
        return {"status": "error", "message": str(e)}


@router.get("/all/{app_name}/{page_name}/")
def get_all_files_req(app_name, page_name):
    if not (re.match(FILE_NAME_REGEX, app_name) and re.match(FILE_NAME_REGEX, page_name)):
        raise HTTPException(
            400,
            detail="app_name and file_name must be only use alphanumerics or underscores.",
        )
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    py_files = glob.glob(os.path.join(dir_path, "*.py"))
    py_files = [file for file in py_files if not file.endswith("__init__.py")]
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": py_files + sql_files}
