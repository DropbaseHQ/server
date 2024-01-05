import asyncio

import requests
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.constants import DROPBASE_API_URL, DROPBASE_TOKEN, WORKER_VERSION
from server.controllers.websocket import handle_websocket_requests
from server.routers import (
    app_router,
    component_router,
    edit_cell_router,
    files_router,
    function_router,
    health_router,
    page_router,
    query_router,
    run_python_router,
    run_sql_router,
    sources_router,
    sync_router,
    tables_router,
    widgets_router,
)


# to disable cache for static files
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


app = FastAPI()
origins = ["http://localhost:3030", "http://www.localhost:3030"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static file server for lsp
app.mount("/workspace", NoCacheStaticFiles(directory="workspace"), name="workspace")
# routes for resources
app.include_router(query_router)
app.include_router(function_router)
app.include_router(files_router)
app.include_router(sources_router)
app.include_router(sync_router)
app.include_router(run_sql_router)
app.include_router(run_python_router)
app.include_router(widgets_router)
app.include_router(tables_router)
app.include_router(component_router)
app.include_router(app_router)
app.include_router(edit_cell_router)
app.include_router(health_router)
app.include_router(page_router)


# send health report to dropbase server
async def send_report_continuously():
    while True:
        requests.get(DROPBASE_API_URL + f"/worker/worker_status/{DROPBASE_TOKEN}/{WORKER_VERSION}")
        await asyncio.sleep(300)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_report_continuously())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    handle_websocket_requests(websocket)
