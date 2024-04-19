from fastapi import APIRouter, Depends, WebSocket
from fastapi_jwt_auth import AuthJWT
from dropbase.helpers.display_rules import run_display_rule
from server.requests.dropbase_router import DropbaseRouter, WSDropbaseRouterGetter
from server.utils import auth_module_is_installed

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    Authorize: AuthJWT = Depends(),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        # ======== AUTHENTICATION ======== #
        if auth_module_is_installed:
            if not hasattr(websocket, "authenticated") or not websocket.authenticated:
                if data["type"] == "auth":
                    access_token = data.get("access_token")
                    try:
                        Authorize.jwt_required("websocket", token=access_token)
                        setattr(websocket, "authenticated", True)
                        await websocket.send_json({"authenticated": True})

                    except Exception as e:
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
