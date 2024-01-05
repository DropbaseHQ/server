from fastapi import WebSocket

from server.controllers.display_rules import run_display_rule


async def handle_websocket_requests(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if data["type"] == "display_rule":
            context = run_display_rule(**data["payload"])
            await websocket.send_json({"context": context})
        else:
            await websocket.send_json({"message": f"You sent: {data['message']}"})
