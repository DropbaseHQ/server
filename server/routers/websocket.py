from fastapi import APIRouter, Depends, WebSocket

from dropbase.helpers.display_rules import run_display_rule
from server.requests.dropbase_router import DropbaseRouter, WSDropbaseRouterGetter

router = APIRouter()

dropbase_router_factory = WSDropbaseRouterGetter(access_token="temp")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    dropbase_router: DropbaseRouter = Depends(dropbase_router_factory),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()

        # ======== AUTHENTICATION ======== #
        if not hasattr(websocket, "authenticated") or not websocket.authenticated:
            if data["type"] == "auth":
                access_token = data.get("access_token")
                dropbase_router.set_access_token(access_token=access_token)
                response = dropbase_router.auth.verify_identity_token(access_token)
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
        if data["type"] == "display_rule":
            state_context = data["state_context"]
            state = state_context["state"]
            payload = {"app_name": data["app_name"], "page_name": data["page_name"], "state": state}
            context = run_display_rule(**payload)
            await websocket.send_json({"context": context})
        else:
            message = data.get("message")
            await websocket.send_json({"message": f"You sent: {message}"})
