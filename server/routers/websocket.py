from fastapi import APIRouter, WebSocket

from server.controllers.display_rules import run_display_rule

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if data["type"] == "display_rule":
            state_context = data["state_context"]
            state = state_context["state"]
            context = state_context["context"]
            payload = {
                "app_name": data["app_name"],
                "page_name": data["page_name"],
                "state": state,
                "context": context,
            }
            context = run_display_rule(**payload)
            await websocket.send_json({"context": context})
        else:
            await websocket.send_json({"message": f"You sent: {data['message']}"})
