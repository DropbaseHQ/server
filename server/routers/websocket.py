from fastapi import APIRouter, Depends, WebSocket

from server.controllers.display_rules import run_display_rule
from server.requests.dropbase_router import DropbaseRouter, WSDropbaseRouterGetter

router = APIRouter()

dropbase_router_factory = WSDropbaseRouterGetter(access_token="temp")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if data["type"] == "display_rule":
            state_context = data["state_context"]
            state = state_context["state"]
            payload = {
                "app_name": data["app_name"],
                "page_name": data["page_name"],
                "state": state,
            }
            context = run_display_rule(**payload)
            await websocket.send_json({"context": context})
        else:
            message = data.get("message")
            await websocket.send_json({"message": f"You sent: {message}"})
