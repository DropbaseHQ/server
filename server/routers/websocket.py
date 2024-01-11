from fastapi import APIRouter, WebSocket
from server.controllers.display_rules import run_display_rule
from server.constants import DROPBASE_API_URL
import requests

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()

        # ======== AUTHENTICATION ======== #
        if not hasattr(websocket, "authenticated") or not websocket.authenticated:
            if data["type"] == "auth":
                access_token = data["access_token"]
                response = requests.post(
                    DROPBASE_API_URL + "/worker/verify_token",
                    cookies={"access_token_cookie": access_token},
                )
                if response.status_code == 200:
                    setattr(websocket, "authenticated", True)
                    await websocket.send_json({"authenticated": True})
                else:
                    await websocket.send_json({"authenticated": False})
            else:
                await websocket.send_json({"message": "You are not authenticated"})
            continue
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
            message = data.get("message")
            await websocket.send_json({"message": f"You sent: {message}"})
