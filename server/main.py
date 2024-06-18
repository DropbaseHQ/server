import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from server import routers
from server.constants import CORS_ORIGINS


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

# routes for resources
app.include_router(routers.function_router)
app.include_router(routers.files_router)
app.include_router(routers.sources_router)
app.include_router(routers.component_router)
app.include_router(routers.app_router)
app.include_router(routers.page_router)
app.include_router(routers.websocket_router)
app.include_router(routers.workspace_router)
app.include_router(routers.status_router)


# health check
@app.get("/health/")
async def health_check():
    return {"status": "ok"}


page_logger = logging.getLogger(__name__)


@app.exception_handler(WebSocketDisconnect)
async def websocket_disconnect_exception_handler(request, exc):
    page_logger.info("WebSocket connection closed")
