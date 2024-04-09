import os

from fastapi import APIRouter, Depends

from dropbase.helpers.utils import check_if_object_exists
from server.controllers.workspace import WorkspaceFolderController
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router

router = APIRouter(
    prefix="/worker_workspace",
    tags=["workspace"],
    responses={404: {"description": "Not found"}},
)


# @router.get("/")
# async def get_workspace(router: DropbaseRouter = Depends(get_dropbase_router)) -> dict:

#     workspace_folder_controller = WorkspaceFolderController(
#         r_path_to_workspace=os.path.join(os.getcwd(), "workspace")
#     )
#     # Adds workspace id to workspace properties if not there already
#     if check_if_object_exists("workspace/properties.json"):
#         workspace_props = workspace_folder_controller.get_workspace_properties()
#         workspace_id = workspace_props.get("id")
#         if not workspace_id:
#             remote_id = workspace_info.get("id")
#             if remote_id:
#                 workspace_props["id"] = remote_id
#                 workspace_folder_controller.write_workspace_properties(
#                     {**workspace_props, "id": remote_id}
#                 )
#     return workspace_info
