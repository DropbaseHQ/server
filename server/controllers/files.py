import ast
import glob
import os
import re
import shutil
from uuid import uuid4

from fastapi import HTTPException

from dropbase.constants import FILE_NAME_REGEX
from dropbase.schemas.files import CreateFile, DeleteFile, RenameFile, UpdateFile
from server.constants import cwd
from server.controllers.properties import read_page_properties, write_page_properties


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

    def get_all_files(self):
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
            return {"files": py_files + sql_files}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def create_file(self, req: CreateFile):
        try:
            # set file paths
            self._set_file_name(req.name, req.type)

            # Check for duplicate file names in properties
            self._check_for_duplicate_file_names(req.name)

            # update file content
            boilerplate_code = compose_boilerplate_code(req)
            self._write_file(boilerplate_code)

            # update properties file
            self.properties["files"].append(
                {"name": req.name, "type": req.type, "source": req.source, "depends_on": []}
            )

            # update properties file
            self._update_properties()

            return {"status": "success"}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def rename_file(self, req: RenameFile):
        try:
            self._set_file_name(req.old_name, req.type)

            # if file does not exist, exit
            self._check_file_exists()

            # Check new name is not duplicate
            self._check_for_duplicate_file_names(req.new_name)

            self._set_file_name(req.new_name, req.type, new=True)
            if os.path.exists(self.file_path):
                os.rename(self.file_path, self.new_path)

            if self.file_ext == ".py":
                self._rename_function_in_file()

            for file in self.properties["files"]:
                if file["name"] == self.file_name:
                    file["name"] = self.new_name
                    break

            # update properties file
            self._update_properties(mode="rename")

            return {"status": "success"}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def update_file(self, req: UpdateFile):
        try:
            # set file paths
            self._set_file_name(req.file_name, req.type)
            self._check_file_exists()
            # update file content
            self._write_file(req.code)

            # get depends on tables
            depends_on = req.depends_on if req.depends_on else []
            if req.type == "sql":
                depends_on_tables = self._get_depend_table_names(user_sql=req.code)
                tables = {p["name"]: p for p in self.properties["blocks"] if p["block_type"] == "table"}
                for table_name in depends_on_tables:
                    if tables.get(table_name):
                        depends_on.append(table_name)

            # update file property in properties.json
            for file in self.properties["files"]:
                if file["name"] == req.file_name:
                    file["source"] = req.source
                    file["type"] = req.type
                    file["depends_on"] = depends_on
                    break

            # update properties file
            self._update_properties()
            return {"status": "success"}
        except HTTPException as e:
            self._revert_backup()
            raise e
        except Exception as e:
            self._revert_backup()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self._delete_backup()

    def delete_file(self, req: DeleteFile):
        try:
            # set file paths
            self._set_file_name(req.file_name, req.type)
            # check if file exists
            self._check_file_exists()
            # delete file
            os.remove(self.file_path)

            # remove file from properties
            for file in self.properties["files"]:
                if file["name"] == self.file_name:
                    self.properties["files"].remove(file)
                    break

            # update properties file
            self._update_properties(mode="delete")
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

    def _get_file_path(self, file_name: str, file_type: str):
        file_ext = ".sql" if file_type == "sql" else ".py"
        return cwd + f"/workspace/{self.app_name}/{self.page_name}/scripts/{file_name}{file_ext}"

    def _write_file(self, code: str):
        with open(self.file_path, "w") as f:
            f.write(code)

    def _update_properties(self, mode: str = "update"):
        if mode == "rename":
            # find old file name in table fetcher in properties and update it
            for block in self.properties["blocks"]:
                if block["block_type"] == "table" and block.get("fetcher") == self.file_name:
                    block["fetcher"] = self.new_name
        elif mode == "delete":
            # find file name in table fetcher in properties and delete it
            for block in self.properties["blocks"]:
                if block["block_type"] == "table" and block.get("fetcher") == self.file_name:
                    block["fetcher"] = ""
        write_page_properties(self.app_name, self.page_name, self.properties)

    def _rename_function_in_file(self):
        # get file mame without extension
        old_name = self.file_name
        new_name = self.new_name

        with open(self.new_path, "r") as file:
            file_content = file.read()
        tree = ast.parse(file_content)

        # rename function name in file
        class FunctionRenamer(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == old_name:
                    node.name = new_name
                return node

        tree = FunctionRenamer().visit(tree)
        new_code = ast.unparse(tree)

        with open(self.new_path, "w") as file:
            file.write(new_code)

    def _check_for_duplicate_file_names(self, file_name: str):
        file_names = [file["name"] for file in self.properties["files"]]
        if file_name in file_names:
            raise HTTPException(status_code=400, detail="File with the same name already exists")

    def _check_file_exists(self):
        if not os.path.exists(self.file_path):
            raise HTTPException(status_code=400, detail="The file does not exist")

    def _get_depend_table_names(self, user_sql: str):
        pattern = re.compile(r"\{\{state\.(\w+)\.\w+\}\}")
        matches = pattern.findall(user_sql)
        return list(set(matches))


def compose_boilerplate_code(req: CreateFile):
    if req.type == "ui":
        return f"""from workspace.{req.app_name}.{req.page_name} import Context, State\n\n
def {req.name}(state: State, context: Context) -> Context:
    context.page.message = "Hello World"
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
        return f"""def {req.name}():
    pass
"""
    else:
        return ""
