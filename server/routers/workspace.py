import json
import os

from fastapi import APIRouter, Depends

from dropbase.helpers.utils import check_if_object_exists
from server.controllers.sync import auto_sync_demo, sync_with_dropbase
from server.controllers.workspace import WorkspaceFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/worker_workspace",
    tags=["worker_workspace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:

    # response = router.auth.get_worker_workspace()
    # workspace_info = response.json()
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(os.getcwd(), "workspace")
    )
    # Adds workspace id to workspace properties if not there already
    if check_if_object_exists("workspace/properties.json"):
        workspace_props = workspace_folder_controller.get_workspace_properties()
        # workspace_id = workspace_props.get("id")
        # if not workspace_id:
        #     remote_id = workspace_info.get("id")
        #     if remote_id:
        #         workspace_props["id"] = remote_id
        #         workspace_folder_controller.write_workspace_properties(
        #             {**workspace_props, "id": remote_id}
        #         )
        return workspace_props
    # auto_sync_demo(router=router)
    # sync_with_dropbase(router=router)
    return None


@router.post("/sync")
async def sync_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.sync_worker_workspace()
    workspace_info = response.json()
    # Sync workspace_id to properties.json
    # sync demo here
    # check if demo dicrectory exists
    _ = WorkspaceFolderController(
        r_path_to_workspace=os.path.join(os.getcwd(), "workspace")
    )

    if check_if_object_exists("workspace/demo"):
        # check if already synced
        demo_synced = False
        if check_if_object_exists("workspace/properties.json"):
            with open("workspace/properties.json", "r") as file:
                apps = json.load(file)["apps"]
            for app in apps:
                if app.get("name") == "demo" and app.get("id") != "":
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

                # sync app
                app_record = {
                    "name": "demo",
                    "label": "Demo",
                    "id": response.get("app_id"),
                }
                if not check_if_object_exists("workspace/properties.json"):
                    apps = [app_record]
                else:
                    # using app read from properties.json from above
                    demo_exists = False
                    for app in apps:
                        if app.get("name") == "demo":
                            app["id"] = response.get("app_id")
                            demo_exists = True
                            break
                    if not demo_exists:
                        apps.append(app_record)

                with open("workspace/properties.json", "w") as file:
                    json.dump({"apps": apps}, file)

                # sync pages
                if check_if_object_exists("workspace/demo/properties.json"):
                    with open("workspace/demo/properties.json", "r") as file:
                        pages = json.load(file)["pages"]

                    page_info = response.get("pages")
                    demo_page = page_info[0]
                    for page in pages:
                        if page.get("id") == "":
                            page["id"] = demo_page.get("id")
                            break
                    with open("workspace/demo/properties.json", "w") as file:
                        json.dump({"pages": pages}, file)

    return workspace_info
