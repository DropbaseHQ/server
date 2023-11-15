from fastapi import APIRouter

from server import requests as dropbase_router
from server.controllers.utils import handle_state_context_updates
from server.schemas.widgets import CreateWidget, UpdateWidget

router = APIRouter(prefix="/widgets", tags=["widgets"], responses={404: {"description": "Not found"}})


@router.post("/")
def create_widget_req(req: CreateWidget):
    resp = dropbase_router.create_widget(**req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.put("/{widget_id}/")
def update_widget_req(widget_id: str, req: UpdateWidget):
    resp = dropbase_router.update_widget(widget_id=widget_id, update_data=req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.delete("/{widget_id}/")
def delete_widget_req(widget_id):
    resp = dropbase_router.delete_widget(widget_id=widget_id)
    handle_state_context_updates(resp)
    return resp.json()
