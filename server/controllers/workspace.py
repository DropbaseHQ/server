import os
import shutil

from fastapi import HTTPException

from server.controllers.utils import update_state_context_files
from server.requests.dropbase_router import DropbaseRouter


class AppCreator:
    def __init__(
        self,
        app_object: dict,
        app_template: dict,
        r_path_to_workspace: str,
        dropbase_api_url: str,
        router: DropbaseRouter,
    ):
        self.app_object = app_object
        self.app_template = app_template
        self.r_path_to_workspace = r_path_to_workspace
        self.dropbase_api_url = dropbase_api_url
        self.router = router

    def _create_default_workspace_files(self) -> str | None:
        try:
            app_folder_path = os.path.join(self.r_path_to_workspace, self.app_object.get("name"))

            # Create new app folder
            create_folder(path=app_folder_path)
            create_init_file(path=app_folder_path)

            # Create new page folder with __init__.py
            page_name = self.app_template.get("page").get("name")
            page_folder_path = os.path.join(app_folder_path, page_name)
            create_folder(path=page_folder_path)
            create_init_file(path=page_folder_path, init_code=PAGE_INIT_CODE)

            create_file(path=page_folder_path, content="", file_name="state.py")
            create_file(path=page_folder_path, content="", file_name="context.py")

            # Create new scripts folder with __init__.py
            scripts_folder_name = "scripts"
            scripts_folder_path = os.path.join(page_folder_path, scripts_folder_name)
            create_folder(path=scripts_folder_path)
            create_init_file(path=scripts_folder_path, init_code="")

        except Exception as e:
            print("Unable to create app folder", e)
            raise HTTPException(status_code=500, detail="Unable to create app folder")

    def _get_initial_state_and_context(self, token: str):
        try:
            page_name = self.app_template.get("page").get("name")
            resp = self.router.misc.sync_components(
                app_name=self.app_object.get("name"),
                page_name=page_name,
                token=token,
            )
            response_data = resp.json()
            if resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Unable to sync components")

            update_state_context_files(
                self.app_object.get("name"),
                page_name,
                response_data.get("state"),
                response_data.get("context"),
            )
        except Exception as e:
            print("Unable to update app state and context", e)
            raise HTTPException(status_code=500, detail="Unable to update app state and context")

    def _update_app_draft_status(self):
        new_app_path = os.path.join(self.r_path_to_workspace, self.app_object.get("name"))
        app_id = self.app_object.get("id")
        create_app_response = self.router.app.update_app(app_id, {"is_draft": False})
        if create_app_response.status_code != 200:
            shutil.rmtree(new_app_path)
            raise HTTPException(status_code=500, detail="Unable to create app")

    def create(self):
        self._create_default_workspace_files()
        self._get_initial_state_and_context(token=os.getenv("DROPBASE_TOKEN"))
        self._update_app_draft_status()
        return {"success": True, "app_id": self.app_object.get("id")}


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
