import json
import os
import shutil
import uuid

from fastapi import HTTPException

from server.controllers.generate_models import create_state_context_files
from server.controllers.utils import check_if_object_exists, validate_column_name
from server.requests.dropbase_router import DropbaseRouter

APP_PROPERTIES_TEMPLATE = {
    "pages": [],
}

PAGE_PROPERTIES_TEMPLATE = {
    "tables": [{"name": "table1", "label": "Table 1", "type": "sql", "columns": []}],
    "widgets": [],
    "files": [],
}


class WorkspaceFolderController:
    def __init__(self, r_path_to_workspace: str):
        self.r_path_to_workspace = r_path_to_workspace

    def write_workspace_properties(self, workspace_properties: dict):
        workspace_properties_path = os.path.join(self.r_path_to_workspace, "properties.json")
        with open(workspace_properties_path, "w") as file:
            json.dump(workspace_properties, file, indent=2)

    def get_workspace_properties(self):
        if os.path.exists(os.path.join(self.r_path_to_workspace, "properties.json")):
            with open(os.path.join(self.r_path_to_workspace, "properties.json"), "r") as file:

                props = json.load(file)
                return props.get("apps", [])

        return None

    def get_app(self, app_id: str):
        workspace_data = self.get_workspace_properties()
        for app in workspace_data:
            if app.get("id") == app_id:
                return app
        return None

    def get_app_id(self, app_name: str):
        workspace_data = self.get_workspace_properties()
        app_id = None
        for app in workspace_data:
            if app.get("name") == app_name:
                app_id = app.get("id", None)
                return app_id

    def update_app_info(self, app_id: str, new_label: str):
        target_app = self.get_app(app_id=app_id)
        if target_app is None:
            raise HTTPException(
                status_code=400, detail="App does not exist, or id does not exist for this app."
            )

        existing_app_labels = [a["label"] for a in self.get_workspace_properties()]

        if new_label in existing_app_labels:
            raise HTTPException(status_code=400, detail="Another app with the same label already exists")

        app_info = {**target_app, "label": new_label}
        workspace_data = self.get_workspace_properties()
        for app in workspace_data:
            if app.get("id") == app_id:
                app.update(app_info)
                break
        self.write_workspace_properties({"apps": workspace_data})


class AppFolderController:
    def __init__(
        self,
        app_name: str,
        r_path_to_workspace: str,
    ):
        self.app_name = app_name
        self.page_name = "page1"
        self.page_label = "Page1"
        self.r_path_to_workspace = r_path_to_workspace
        self.app_folder_path = os.path.join(self.r_path_to_workspace, self.app_name)
        self.page_properties = PAGE_PROPERTIES_TEMPLATE

    def _get_app_properties_data(self):
        path_to_app_properties = os.path.join(self.app_folder_path, "properties.json")
        if not os.path.exists(path_to_app_properties):
            return None
        with open(path_to_app_properties, "r") as file:
            return json.load(file)

    def _write_app_properties_data(self, app_properties_data: dict):
        path_to_app_properties = os.path.join(self.app_folder_path, "properties.json")
        with open(path_to_app_properties, "w") as file:
            json.dump(app_properties_data, file, indent=2)

    def _get_workspace_properties(self):
        workspace_properties_path = os.path.join(self.r_path_to_workspace, "properties.json")
        if not os.path.exists(workspace_properties_path):
            return None
        with open(workspace_properties_path, "r") as file:
            return json.load(file)

    def _write_workspace_properties(self, workspace_properties: dict):
        workspace_properties_path = os.path.join(self.r_path_to_workspace, "properties.json")
        with open(workspace_properties_path, "w") as file:
            json.dump(workspace_properties, file, indent=2)

    def _add_page_to_app_properties(self, page_name: str, page_label: str):
        app_properties_data = self._get_app_properties_data()

        page_object = {
            "name": page_name,
            "label": page_label,
            "id": str(uuid.uuid4()),
        }
        if "pages" in app_properties_data:
            app_properties_data["pages"].append(page_object)
        else:
            app_properties_data["pages"] = [page_object]

        self._write_app_properties_data(app_properties_data)
        return page_object

    def _add_app_to_workspace_properties(self, app_name: str, app_label: str = None):
        workspace_properties = self._get_workspace_properties()
        app_object = {
            "name": app_name,
            "label": app_label if app_label else app_name,
            "id": str(uuid.uuid4()),
        }
        if "apps" in workspace_properties:
            workspace_properties["apps"].append(app_object)
        else:
            workspace_properties["apps"] = [app_object]

        self._write_workspace_properties(workspace_properties)
        return app_object

    def _create_default_workspace_files(
        self, router: DropbaseRouter, app_label: str = None
    ) -> str | None:
        try:
            # Create new app folder
            create_folder(path=self.app_folder_path)
            create_init_file(path=self.app_folder_path)

            app_object = self._add_app_to_workspace_properties(
                app_name=self.app_name, app_label=app_label
            )

            new_app_properties = self._get_app_properties()
            create_file(
                path=self.app_folder_path,
                content=json.dumps(new_app_properties, indent=2),
                file_name="properties.json",
            )
            if router:
                router.app.create_app(app_properties={**app_object})

            # Create new page folder with __init__.py
            self.create_page(router=router)

        except Exception as e:
            print("Unable to create app folder", e)
            raise HTTPException(status_code=500, detail="Unable to create app folder")

    def _get_app_properties(self):
        new_app_properties = APP_PROPERTIES_TEMPLATE

        return new_app_properties

    def get_app_id(self, app_name: str):
        workspace_data = self._get_workspace_properties()
        app_id = None
        for app in workspace_data.get("apps", []):
            if app.get("name") == self.app_name:
                app_id = app.get("id", None)
                return app_id

    def create_workspace_properties(self):
        if os.path.exists(os.path.join(self.r_path_to_workspace, "properties.json")):
            return

        created_app_names = get_subdirectories(self.r_path_to_workspace)
        app_info = []
        for app_name in created_app_names:
            app_properties = os.path.join(self.r_path_to_workspace, app_name, "properties.json")
            if not os.path.exists(app_properties):
                app_info.append({"name": app_name, "label": app_name, "id": None})
                continue

            app_object = {}
            with open(app_properties, "r") as file:
                app_props = json.load(file)
                app_object["name"] = app_props.get("app_name")
                app_object["label"] = app_props.get("app_label")
                app_object["id"] = app_props.get("app_id")
            app_info.append(app_object)

        create_file(
            path=self.r_path_to_workspace,
            content=json.dumps({"apps": app_info}, indent=2),
            file_name="properties.json",
        )

    def create_page(
        self,
        router: DropbaseRouter = None,
        app_folder_path: str = None,
        page_name: str = None,
        page_label: str = None,
    ):
        app_folder_path = app_folder_path or self.app_folder_path
        page_name = page_name or self.page_name
        page_label = page_label or self.page_label

        if not validate_column_name(page_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid page name. Only alphanumeric characters and underscores are allowed",
            )

        if check_if_object_exists(os.path.join(app_folder_path, page_name)):
            raise HTTPException(
                status_code=400,
                detail="Another page with the same name already exists",
            )

        existing_page_labels = [p["label"] for p in self.get_pages()]

        if page_label in existing_page_labels:
            raise HTTPException(
                status_code=400,
                detail="Another page with the same label already exists",
            )

        # Create new page folder with __init__.py
        page_folder_path = os.path.join(app_folder_path, page_name)

        create_folder(path=page_folder_path)
        create_init_file(path=page_folder_path, init_code=PAGE_INIT_CODE)

        create_file(path=page_folder_path, content="", file_name="state.py")
        create_file(path=page_folder_path, content="", file_name="context.py")
        # create properties.json
        create_file(
            path=page_folder_path,
            content=json.dumps(self.page_properties, indent=2),
            file_name="properties.json",
        )

        # Create new scripts folder with __init__.py
        scripts_folder_name = "scripts"
        scripts_folder_path = os.path.join(page_folder_path, scripts_folder_name)
        create_folder(path=scripts_folder_path)
        create_init_file(path=scripts_folder_path, init_code="")

        create_state_context_files(self.app_name, page_name, self.page_properties)
        page_object = self._add_page_to_app_properties(page_name, page_label)
        app_id = self.get_app_id(self.app_name)
        create_page_payload = {
            "app_id": app_id,
            **page_object,
        }
        if router:
            router.page.create_page(page_properties=create_page_payload)

        return {"message": "Page created"}

    def rename_page(self, page_name: str, new_page_label: str):
        existing_page_labels = [p["label"] for p in self.get_pages()]

        if new_page_label in existing_page_labels:
            raise HTTPException(
                status_code=400,
                detail="Another page with the same label already exists",
            )

        # rename page in properties.json
        app_properties_data = self._get_app_properties_data()
        for page in app_properties_data["pages"]:
            if page["name"] == page_name:
                page["label"] = new_page_label
                break

        self._write_app_properties_data(app_properties_data)
        return {"message": "Page renamed"}

    def delete_page(self, page_name: str, router: DropbaseRouter):

        # check properties.json first
        app_properties_data = self._get_app_properties_data()
        if not app_properties_data:
            return

        if len(app_properties_data["pages"]) == 1:
            raise HTTPException(
                status_code=400, detail="Cannot delete the only page in the app. Delete the app instead."
            )

        # delete page folder
        page_folder_path = os.path.join(self.app_folder_path, page_name)
        shutil.rmtree(page_folder_path)

        # delete page from properties.json
        page_id = None
        for page in app_properties_data["pages"]:
            if page["name"] == page_name:
                page_id = page.get("id", None)
                app_properties_data["pages"].remove(page)
                break

        self._write_app_properties_data(app_properties_data)
        router.page.delete_page(page_id=page_id)

        return {"message": "Page deleted"}

    def get_pages(self):
        if os.path.exists(os.path.join(self.app_folder_path, "properties.json")):
            return self._get_app_properties_data().get("pages", [])

        page_names = get_subdirectories(self.app_folder_path)
        pages = [{"name": page} for page in page_names]
        return pages

    def create_app(self, app_label: str = None, router: DropbaseRouter = None):
        if not validate_column_name(self.app_name):
            raise HTTPException(
                status_code=400,
                detail="Invalid app name. Only alphanumeric characters and underscores are allowed",
            )

        if check_if_object_exists(self.app_folder_path):
            raise HTTPException(status_code=400, detail="Another app with the same name already exists")

        existing_app_labels = [a["label"] for a in self._get_workspace_properties()["apps"]]

        if app_label in existing_app_labels:
            raise HTTPException(status_code=400, detail="Another app with the same label already exists")

        self.create_workspace_properties()
        self._create_default_workspace_files(router=router, app_label=app_label)

        return {"success": True}

    def delete_app(self, app_name: str, router: DropbaseRouter):
        app_path = os.path.join(self.r_path_to_workspace, app_name)
        if os.path.exists(app_path):
            shutil.rmtree(app_path)

            workspace_properties = self._get_workspace_properties()
            if not workspace_properties:
                return

            app_id = None
            for app in workspace_properties["apps"]:
                if app["name"] == app_name:
                    app_id = app.get("id", None)
                    workspace_properties["apps"].remove(app)
                    break

            self._write_workspace_properties(workspace_properties)
            router.app.delete_app(app_id=app_id)
            return {"message": "App deleted"}
        else:
            raise HTTPException(status_code=400, detail="App does not exist")


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
    # NOTE: this is a dangerous function, let's add some checks
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


def get_subdirectories(path):
    return [
        name
        for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name)) and name != "__pycache__"
    ]
