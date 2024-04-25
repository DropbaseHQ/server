import ast
import glob
import os
import re
import shutil
from uuid import uuid4

from fastapi import HTTPException

from dropbase.constants import FILE_NAME_REGEX
from dropbase.helpers.utils import read_page_properties
from dropbase.schemas.files import UpdateFile
from server.constants import cwd


class FileController:
    def __init__(self, app_name: str, page_name: str):
        self.app_name = app_name
        self.page_name = page_name
        self.properties = read_page_properties(app_name, page_name)
        self.file_ext = None
        self.file_name = None
        self.file_path = None
        self.new_name = None
        self.new_path = None
        # create a backup of the page directory
        self.page_dir_path = f"workspace/{self.app_name}/{self.page_name}"
        self.page_dir_path_backup = f"{self.page_dir_path}_{uuid4().hex}"
        shutil.copytree(self.page_dir_path, self.page_dir_path_backup)

    def _revert_backup(self):
        shutil.rmtree(self.page_dir_path)
        os.rename(self.page_dir_path_backup, self.page_dir_path)

    def _delete_backup(self):
        if os.path.isdir(self.page_dir_path_backup):
            shutil.rmtree(self.page_dir_path_backup)

    def get_all_files(self, python: bool = True, sql: bool = True):
        try:
            if not (
                re.match(FILE_NAME_REGEX, self.app_name) and re.match(FILE_NAME_REGEX, self.page_name)
            ):  # noqa
                raise HTTPException(
                    status_code=400,
                    detail="No files found. Please check if the app name and page name are valid.",
                )
            dir_path = cwd + f"/workspace/{self.app_name}/{self.page_name}/scripts"
            py_files = glob.glob(os.path.join(dir_path, "*.py"))
            py_files = [file for file in py_files if not file.endswith("__init__.py")]
            sql_files = glob.glob(os.path.join(dir_path, "*.sql"))

            if python and not sql:
                return {"files": py_files}
            if sql and not python:
                return {"files": sql_files}
            return {"files": py_files + sql_files}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def get_functions(self):
        functions = []
        python_data = self.get_all_files(sql=False)  # files are a list of strings
        python_files = python_data["files"]
        for file in python_files:
            file_name = file.split("/")[-1].split(".")[0]
            with open(file, "r") as source_file:
                source_code = source_file.read()

            parsed_code = ast.parse(source_code)

            for node in ast.walk(parsed_code):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has 'state' and 'context' in arguments and returns 'context'
                    args = {arg.arg: getattr(arg.annotation, "id", None) for arg in node.args.args}
                    has_state_and_context = (
                        "state" in args
                        and args["state"] == "State"
                        and "context" in args
                        and args["context"] == "Context"
                    )
                    returns_context = isinstance(node.returns, ast.Name) and node.returns.id == "Context"

                    if has_state_and_context and returns_context:
                        functions.append({"value": node.name, "type": "function", "file": file_name})

        sql_data = self.get_all_files(python=False)
        sql_files = sql_data["files"]
        for file in sql_files:
            file_name = file.split("/")[-1].split(".")[0]
            functions.append({"value": file_name, "type": "sql"})
        return functions

    def update_file(self, req: UpdateFile):
        try:
            # set file paths
            self._set_file_name(req.file_name, req.type)
            self._check_file_exists()
            # update file content
            self._write_file(req.code)

            return {"status": "success"}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def _set_file_name(self, file_name: str, file_type: str, new: bool = False):
        self.file_ext = ".sql" if file_type == "sql" else ".py"
        file_name = file_name
        file_path = (
            cwd + f"/workspace/{self.app_name}/{self.page_name}/scripts/{file_name + self.file_ext}"
        )
        if new:
            self.new_name = file_name
            self.new_path = file_path
        else:
            self.file_name = file_name
            self.file_path = file_path

    def _write_file(self, code: str):
        with open(self.file_path, "w") as f:
            f.write(code)

    def _check_file_exists(self):
        if not os.path.exists(self.file_path):
            raise HTTPException(status_code=400, detail="The file does not exist")
