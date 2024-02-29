import asyncio
import json
import logging

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.constants import CORS_ORIGINS, DROPBASE_API_URL, DROPBASE_TOKEN, WORKER_VERSION
from server.routers import (
    app_router,
    component_router,
    edit_cell_router,
    files_router,
    function_router,
    health_router,
    page_router,
    query_router,
    sources_router,
    tables_router,
    websocket_router,
    workspace_router,
)


# to disable cache for static files
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


spam_urls = ["/health/"]


class LogSpamFilter(logging.Filter):
    def filter(self, record):
        for url in spam_urls:
            if url in record.args:
                return False
        return True


logger = logging.getLogger("uvicorn.access")
logger.addFilter(LogSpamFilter())

app = FastAPI()
origins = json.loads(CORS_ORIGINS)

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
# app.include_router(run_sql_router)
# app.include_router(run_python_router)
app.include_router(tables_router)
app.include_router(component_router)
app.include_router(app_router)
app.include_router(edit_cell_router)
app.include_router(health_router)
app.include_router(page_router)
app.include_router(websocket_router)
app.include_router(workspace_router)


# send health report to dropbase server
async def send_report_continuously():
    while True:
        requests.get(DROPBASE_API_URL + f"/worker/worker_status/{DROPBASE_TOKEN}/{WORKER_VERSION}")
        await asyncio.sleep(300)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_report_continuously())
