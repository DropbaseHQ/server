from server.routers.app import router as app_router
from server.routers.components import router as component_router
from server.routers.files import router as files_router
from server.routers.function import router as function_router
from server.routers.page import router as page_router
from server.routers.sources import router as sources_router
from server.routers.status import router as status_router
from server.routers.websocket import router as websocket_router

__all__ = [
    "files_router",
    "function_router",
    "sources_router",
    "app_router",
    "component_router",
    "page_router",
    "websocket_router",
    "status_router",
]
