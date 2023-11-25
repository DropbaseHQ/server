from fastapi import APIRouter, Depends
from server.controllers.utils import handle_state_context_updates
from server.schemas.widgets import CreateWidget, UpdateWidget
from server.requests.dropbase_router import DropbaseRouter, get_dropbase_router


router = APIRouter(
    prefix="/widgets", tags=["widgets"], responses={404: {"description": "Not found"}}
)


@router.post("/")
def create_widget_req(
    req: CreateWidget, router: DropbaseRouter = Depends(get_dropbase_router)
):
    resp = router.widget.create_widget(**req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.put("/{widget_id}/")
def update_widget_req(
    widget_id: str,
    req: UpdateWidget,
    router: DropbaseRouter = Depends(get_dropbase_router),
):
    resp = router.widget.update_widget(widget_id=widget_id, update_data=req.dict())
    handle_state_context_updates(resp)
    return resp.json()


@router.delete("/{widget_id}/")
def delete_widget_req(widget_id, router: DropbaseRouter = Depends(get_dropbase_router)):
    resp = router.widget.delete_widget(widget_id=widget_id)
    handle_state_context_updates(resp)
    return resp.json()
