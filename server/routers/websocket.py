import asyncio

import requests
from fastapi import APIRouter, WebSocket

from server.constants import DROPBASE_API_URL
from server.controllers.display_rules import run_display_rule

router = APIRouter()


async def check_for_new_db_data(websocket):
    i = 0
    while True:
        i += 1
        new_data = i  # Non-blocking DB read here
        if new_data:
            await websocket.send_text(f"New data: {new_data}")
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)  # Can be adjusted based on your needs


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    asyncio.create_task(check_for_new_db_data(websocket))  # Run database check async.
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
                await websocket.send_json(
                    {
                        "message": "You are not authenticated",
                        "type": "auth_error",
                        "failed_data": data,
                    }
                )
            continue

        # ======== DISPLAY RULE ======== #
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
