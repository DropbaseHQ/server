from fastapi import APIRouter, WebSocket

from dropbase.helpers.display_rules import run_display_rule

router = APIRouter()


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
