import glob
import json
import os
import re

from fastapi import APIRouter, HTTPException, Response

from server.constants import FILE_NAME_REGEX, cwd
from server.controllers.files import create_file
from server.controllers.query import get_sql_variables
from server.controllers.utils import rename_function_in_file
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
        properties_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/properties.json"
        with open(properties_path, "r") as f:
            properties = json.load(f)

        for file in properties["files"]:
            if file["name"] == req.old_name:
                file["name"] = req.new_name
                break

        with open(properties_path, "w") as f:
            json.dump(properties, f, indent=2)

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.put("/{file_id}")
def update_file_req(req: UpdateFile, response: Response):
    try:
        file_extension = ".sql" if req.type == "sql" else ".py"
        file_name = req.name
        if not req.name.endswith(file_extension):
            file_name = req.name + file_extension

        # update file content
        file_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        with open(file_path, "w") as f:
            f.write(req.sql)

        # update properties.json
        properties_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/properties.json"
        with open(properties_path, "r") as f:
            properties = json.load(f)

        if req.type == "sql":
            # update depends on flags in properties.json
            depends_on = get_sql_variables(user_sql=req.sql)

            for file in properties["tables"]:
                if file["data_fetcher"] == file_name:
                    file["depends_on"] = depends_on

        # update file property in properties.json
        for file in properties["files"]:
            if file["name"] == req.name:
                file["source"] = req.source
                file["type"] = req.type
                break

        with open(properties_path, "w") as f:
            json.dump(properties, f, indent=2)

        return {"status": "success"}
    except Exception as e:
        response.status_code = 500
        return {"message": str(e)}


@router.delete("/{file_id}/")
def delete_file_req(file_id: str, req: DeleteFile, response: Response):
    try:
        path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{req.file_name}"
        if not os.path.exists(path):
            response.status_code = 400
            return {"status": "error", "message": "The file does not exist"}

        os.remove(path)

        # update properties.json
        properties_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/properties.json"
        with open(properties_path, "r") as f:
            properties = json.load(f)

        for file in properties["files"]:
            if file["name"] == req.file_name:
                properties["files"].remove(file)
                break

        with open(properties_path, "w") as f:
            json.dump(properties, f, indent=2)

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
