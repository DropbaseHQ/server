import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.controllers.utils import check_if_object_exists
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
from server.controllers.sync import sync_with_dropbase, auto_sync_demo

router = APIRouter(
    prefix="/worker_workspace",
    tags=["workspace"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.get_worker_workspace()
    workspace_info = response.json()
    auto_sync_demo(router=router)
    sync_with_dropbase(router=router)
    return workspace_info


@router.post("/sync")
async def sync_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:
    response = router.auth.sync_worker_workspace()
    workspace_info = response.json()
    # sync demo here
    # check if demo dicrectory exists
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
