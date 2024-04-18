import asyncio
import logging

from importlib.util import find_spec
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from server import routers
from server.constants import (
    CORS_ORIGINS,
    DROPBASE_API_URL,
    DROPBASE_TOKEN,
    WORKER_VERSION,
)


# to disable cache for static files
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


class LogSpamFilter(logging.Filter):
    def filter(self, record):
        for url in ["/health/"]:
            if url in record.args:
                return False
        return True


logger = logging.getLogger("uvicorn.access")
logger.addFilter(LogSpamFilter())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# static file server for lsp
app.mount("/workspace", NoCacheStaticFiles(directory="workspace"), name="workspace")

if find_spec("server.auth"):
    from server.auth.endpoints import premium_router

    app.include_router(premium_router)
# routes for resources
app.include_router(routers.query_router)
app.include_router(routers.function_router)
app.include_router(routers.files_router)
app.include_router(routers.sources_router)
app.include_router(routers.tables_router)
app.include_router(routers.component_router)
app.include_router(routers.app_router)
app.include_router(routers.edit_cell_router)
app.include_router(routers.health_router)
app.include_router(routers.page_router)
app.include_router(routers.websocket_router)
app.include_router(routers.workspace_router)


page_logger = logging.getLogger(__name__)


@app.exception_handler(WebSocketDisconnect)
async def websocket_disconnect_exception_handler(request, exc):
    page_logger.info("WebSocket connection closed")


# send health report to dropbase server
async def send_report_continuously():
    # while True:
    #     worker_status_url = (
    #         DROPBASE_API_URL
    #         + f"/worker/worker_status/{DROPBASE_TOKEN}/{WORKER_VERSION}"
    #     )
    #     requests.get(worker_status_url)
    #     await asyncio.sleep(300)
    pass


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_report_continuously())
