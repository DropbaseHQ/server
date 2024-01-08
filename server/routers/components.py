from fastapi import APIRouter  # , Depends, Response

from server.controllers.components import get_component_properties

# from server.controllers.utils import handle_state_context_updates, update_state_context_files
# from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router
# from server.schemas.components import CreateComponent, UpdateComponent

router = APIRouter(
    prefix="/components",
    tags=["components"],
    responses={404: {"description": "Not found"}},
)


@router.get("/properties/{component_type}")
def get_state_context_req(component_type: str):
    return get_component_properties(component_type)


# @router.post("/")
# def create_component_req(
#     req: CreateComponent,
#     response: Response,
#     router: DropbaseRouter = Depends(get_dropbase_router),
# ):
#     resp = router.component.create_component(req.dict())
#     if resp.status_code != 200:
#         response.status_code = resp.status_code
#         return resp.text

#     resp = resp.json()
#     state_context = resp.get("state_context")
#     update_state_context_files(**state_context)
#     return resp.get("component")


# @router.put("/{component_id}/")
# def update_component_req(
#     component_id: str,
#     req: UpdateComponent,
#     router: DropbaseRouter = Depends(get_dropbase_router),
# ):
#     resp = router.component.update_component(component_id=component_id, update_data=req.dict())
#     handle_state_context_updates(resp)
#     return resp.json()


# @router.delete("/{component_id}/")
# def delete_component_req(
#     component_id, response: Response, router: DropbaseRouter = Depends(get_dropbase_router)
# ):
#     resp = router.component.delete_component(component_id=component_id)
#     if resp.status_code != 200:
#         response.status_code = resp.status_code
#         return resp.text
#     handle_state_context_updates(resp)
#     return resp.json()
