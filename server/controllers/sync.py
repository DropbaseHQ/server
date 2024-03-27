import logging
import os
import time
from server.controllers.workspace import WorkspaceFolderController
from server.controllers.app import AppFolderController
from server.requests.dropbase_router import DropbaseRouter
from server.controllers.utils import check_if_object_exists

logger = logging.getLogger(__name__)
cwd = os.getcwd()

sync_interval = 900  # 15 minutes
last_sync_time = 0


def sync_with_dropbase(router: DropbaseRouter):
    current_time = time.time()
    global last_sync_time
    if current_time - last_sync_time < sync_interval:
        return
    last_sync_time = current_time

    # Get all workspace info, including workspace, apps, and their pages
    workspace_path = os.path.join(cwd, "workspace")
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=workspace_path
    )
    workspace_props = workspace_folder_controller.get_workspace_properties()
    workspace_apps = workspace_props.get("apps", [])
    workspace_app_structure = []

    for app in workspace_apps:
        if app.get("name") is None:
            continue

        app_structure = {
            "id": app.get("id"),
            "name": app.get("name"),
        }

        app_folder_controller = AppFolderController(
            app_name=app.get("name"),
            r_path_to_workspace=workspace_path,
        )
        app_properties = app_folder_controller._get_app_properties_data()

        if not app_properties:
            workspace_app_structure.append(app_structure)
            continue

        page_info = app_properties.get("pages", [])

        app_structure["pages"] = page_info
        workspace_app_structure.append(app_structure)
    workspace_structure = {"apps": workspace_app_structure}

    structure_response = router.misc.sync_structure(workspace_structure)
    if structure_response.status_code != 200:
        logger.info("Failed to sync workspace structure")
        return

    try:
        structure_response = structure_response.json()
    except Exception as e:
        logger.info(f"Error parsing response from server: {e}")
        return

    apps_without_ids = structure_response.get("apps_without_id")
    app_with_ids = structure_response.get("apps_with_id")

    workspace_props = workspace_folder_controller.get_workspace_properties()
    properties = workspace_props.get("apps", [])
    for app in apps_without_ids:
        for app_properties in properties:
            if app_properties.get("name") == app.get("name"):
                app_properties["status"] = "ID_NOT_FOUND_BUT_NAME_FOUND"
                break
            app_properties["status"] = "ID_NOT_FOUND_AND_NAME_NOT_FOUND"

    for app in properties:
        if app.get("id") in app_with_ids:
            app["status"] = "SYNCED"
            continue

    workspace_folder_controller.write_workspace_properties(
        {**workspace_props, "apps": properties}
    )


def auto_sync_demo(router: DropbaseRouter):
    if check_if_object_exists("workspace/demo"):
        # check if already synced
        demo_synced = False
        if check_if_object_exists("workspace/properties.json"):
            workspace_folder_controller = WorkspaceFolderController(
                r_path_to_workspace=os.path.join(cwd, "workspace")
            )
            workspace_props = workspace_folder_controller.get_workspace_properties()
            apps = workspace_props.get("apps", [])
            for app in apps:
                if app.get("name") == "demo" and app.get("id"):
                    demo_synced = True
                    break

        if not demo_synced:
            # call server to sync demo
            resp = router.misc.sync_app(
                payload={
                    "app_name": "demo",
                    "app_label": "Demo",
                    "generate_new": True,
                    "pages": [
                        {
                            "name": "demo",
                            "label": "Demo",
                            "id": "",
                        }
                    ],
                }
            )
            if resp.status_code == 200:
                response = resp.json()
                response_app_id = response.get("app_id")

                # sync app
                app_record = {
                    "name": "demo",
                    "label": "Demo",
                    "id": response_app_id,
                }
                if not check_if_object_exists("workspace/properties.json"):
                    apps = [app_record]
                else:
                    # using app read from properties.json from above
                    demo_exists = False
                    for app in apps:
                        if app.get("name") == "demo":
                            app["id"] = response_app_id
                            demo_exists = True
                            break
                    if not demo_exists:
                        apps.append(app_record)

                workspace_folder_controller.write_workspace_properties(
                    {**workspace_props, "apps": apps}
                )

                # sync pages
                if check_if_object_exists("workspace/demo/properties.json"):

                    app_folder_controller = AppFolderController(
                        app_name="demo",
                        r_path_to_workspace=os.path.join(cwd, "workspace"),
                    )
                    properties = app_folder_controller._get_app_properties_data()
                    pages = properties.get("pages", [])
                    page_info = response.get("pages")
                    demo_page = page_info[0]
                    for page in pages:
                        if page.get("id") == "":
                            page["id"] = demo_page.get("id")
                            break

                    app_folder_controller._write_app_properties_data({"pages": pages})
