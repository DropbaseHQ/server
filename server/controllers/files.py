import glob
import os
import re

from fastapi import HTTPException

from server.constants import FILE_NAME_REGEX, cwd
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.query import get_depend_table_names
from server.controllers.utils import rename_function_in_file
from server.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile


def create_file(req: CreateFile):
    # create file in a local workspace
    file_name = req.name + ".sql" if req.type == "sql" else req.name + ".py"
    path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
    boilerplate_code = compose_boilerplate_code(req)

    with open(path, "a") as f:
        f.write(boilerplate_code)

    # update properties.json
    properties = read_page_properties(req.app_name, req.page_name)
    properties["files"].append(
        {"name": req.name, "type": req.type, "source": req.source, "depends_on": []}
    )

    file_names = set()

    # Check for duplicate file names in properties
    for file in properties["files"]:
        if file["name"] in file_names:
            raise HTTPException(status_code=400, detail="File with the same name already exists")

        file_names.add(file["name"])

    # update properties file
    update_properties(req.app_name, req.page_name, properties, update_modes=False)

    return {"status": "success"}


def compose_boilerplate_code(req: CreateFile):
    if req.type == "ui":
        return f"""from workspace.{req.app_name}.{req.page_name} import Context, State\n\n
def {req.name}(state: State, context: Context) -> Context:
    context.widgets.widget1.message = "Hello World"
    return context
"""
    elif req.type == "data_fetcher":
        return f"""from workspace.{req.app_name}.{req.page_name} import State
import pandas as pd\n\n
def {req.name}(state: State) -> pd.DataFrame:
    df = pd.DataFrame()
    return df
"""
    elif req.type == "python":
        return """
def function():
  print("This is a generic Python function")

"""
    else:
        return ""


def rename_file(req: RenameFile):
    file_ext = ".sql" if req.type == "sql" else ".py"
    file_name = req.old_name + file_ext
    file_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"

    # if file does not exist, exit
    if not os.path.exists(file_path):
        raise Exception("The file does not exist")

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

    # update properties file
    update_properties(req.app_name, req.page_name, properties, update_modes=False)

    return {"status": "success"}


def update_file(function_name: str, req: UpdateFile):
    file_extension = ".sql" if req.type == "sql" else ".py"
    file_name = function_name + file_extension

    # update file content
    file_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
    with open(file_path, "w") as f:
        f.write(req.code)

    # update properties.json
    properties = read_page_properties(req.app_name, req.page_name)

    depends_on = req.depends_on if req.depends_on else []
    if req.type == "sql":
        # update depends on flags in properties.json
        depends_on = get_depend_table_names(user_sql=req.code)

    # update file property in properties.json
    for file in properties["files"]:
        if file["name"] == function_name:
            file["source"] = req.source
            file["type"] = req.type
            file["depends_on"] = depends_on
            break

    # update properties file
    update_properties(req.app_name, req.page_name, properties, update_modes=False)

    return {"status": "success"}


def delete_file(req: DeleteFile):
    function_name = req.file_name[:-4] if req.type == "sql" else req.file_name[:-3]
    path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{req.file_name}"
    if not os.path.exists(path):
        raise Exception("The file does not exist")

    os.remove(path)

    properties = read_page_properties(req.app_name, req.page_name)

    for file in properties["files"]:
        if file["name"] == function_name:
            properties["files"].remove(file)
            break

    # update properties file
    update_properties(req.app_name, req.page_name, properties, update_modes=False)

    return {"status": "success"}


def get_all_files(app_name: str, page_name: str):
    if not (re.match(FILE_NAME_REGEX, app_name) and re.match(FILE_NAME_REGEX, page_name)):
        raise Exception("No files found. Please check if the app name and page name are valid.")
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    py_files = glob.glob(os.path.join(dir_path, "*.py"))
    py_files = [file for file in py_files if not file.endswith("__init__.py")]
    sql_files = glob.glob(os.path.join(dir_path, "*.sql"))
    return {"files": py_files + sql_files}
