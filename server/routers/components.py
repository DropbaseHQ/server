from fastapi import APIRouter, Response

from server import requests as dropbase_router
from server.controllers.utils import handle_state_context_updates, update_state_context_files
from server.schemas.components import CreateComponent, UpdateComponent

router = APIRouter(
    prefix="/components", tags=["components"], responses={404: {"description": "Not found"}}
)


@router.post("/")
def create_component_req(req: CreateComponent, response: Response):
    resp = dropbase_router.create_component(req.dict())
    if resp.status_code != 200:
        response.status_code = resp.status_code
        return resp.text

    resp = resp.json()
    state_context = resp.get('state_context')
    update_state_context_files(**state_context)
    return resp.get('component')


@router.put("/{component_id}/")
def update_component_req(component_id: str, req: UpdateComponent):
    resp = dropbase_router.update_component(component_id=component_id, update_data=req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.delete("/{component_id}/")
def delete_component_req(component_id):
    resp = dropbase_router.delete_component(component_id=component_id)
    handle_state_context_updates(resp)
    return resp.json()
