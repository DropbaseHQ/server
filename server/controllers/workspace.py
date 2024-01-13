import json
import os
import shutil
from fastapi import HTTPException

from server.controllers.generate_models import create_state_context_files

PROPERTIES_TEMPLATE = {
    "tables": [{"name": "table1", "label": "Table 1", "type": "sql", "columns": []}],
    "widgets": [],
    "files": [],
}


class AppCreator:
    def __init__(
        self,
        app_name: str,
        r_path_to_workspace: str,
    ):
        self.app_name = app_name
        self.page_name = "page1"
        self.r_path_to_workspace = r_path_to_workspace
        self.app_folder_path = os.path.join(self.r_path_to_workspace, self.app_name)
        self.properties = PROPERTIES_TEMPLATE

    def create_page(self, app_folder_path: str = None, page_name: str = None):
        app_folder_path = app_folder_path or self.app_folder_path
        page_name = page_name or self.page_name

        # Create new page folder with __init__.py
        page_folder_path = os.path.join(app_folder_path, page_name)

        create_folder(path=page_folder_path)
        create_init_file(path=page_folder_path, init_code=PAGE_INIT_CODE)

        create_file(path=page_folder_path, content="", file_name="state.py")
        create_file(path=page_folder_path, content="", file_name="context.py")
        # create properties.json
        create_file(
            path=page_folder_path,
            content=json.dumps(self.properties, indent=2),
            file_name="properties.json",
        )

        # Create new scripts folder with __init__.py
        scripts_folder_name = "scripts"
        scripts_folder_path = os.path.join(page_folder_path, scripts_folder_name)
        create_folder(path=scripts_folder_path)
        create_init_file(path=scripts_folder_path, init_code="")

        create_state_context_files(self.app_name, page_name, self.properties)

    def rename_page(self, old_page_name: str, new_page_name: str):
        # rename page folder
        old_page_folder_path = os.path.join(self.app_folder_path, old_page_name)
        new_page_folder_path = os.path.join(self.app_folder_path, new_page_name)
        os.rename(old_page_folder_path, new_page_folder_path)

    def _create_default_workspace_files(self) -> str | None:
        try:
            # Create new app folder
            create_folder(path=self.app_folder_path)
            create_init_file(path=self.app_folder_path)

            # Create new page folder with __init__.py
            self.create_page()

        except Exception as e:
            print("Unable to create app folder", e)
            raise HTTPException(status_code=500, detail="Unable to create app folder")

    def create(self):
        self._create_default_workspace_files()
        return {"success": True}


INIT_CODE = """
import importlib
import os
import pkgutil

# import immediate subdirectories, should only import widgets
for importer, modname, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)]):
    module_dir = os.path.join(os.path.dirname(__file__), modname)
    if ispkg and os.path.exists(module_dir):
        importlib.import_module(f".{modname}", __package__)
"""
PAGE_INIT_CODE = """
from .context import Context
from .state import State
"""


def create_file(path, content, file_name):
    path = os.path.join(path, file_name)
    with open(path, "w") as file:
        file.write(content)


def create_init_file(path, init_code=INIT_CODE):
    create_file(path, init_code, "__init__.py")


def create_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
