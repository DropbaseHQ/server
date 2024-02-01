from server.routers.app import router as app_router
from server.routers.components import router as component_router
from server.routers.edit_cell import router as edit_cell_router
from server.routers.files import router as files_router
from server.routers.function import router as function_router
from server.routers.health import router as health_router
from server.routers.page import router as page_router
from server.routers.query import router as query_router

# from server.routers.run_python import router as run_python_router
# from server.routers.run_sql import router as run_sql_router
from server.routers.sources import router as sources_router
from server.routers.tables import router as tables_router
from server.routers.websocket import router as websocket_router

__all__ = [
    "files_router",
    "function_router",
    "query_router",
    # "run_python_router",
    # "run_sql_router",
    "sources_router",
    "tables_router",
    "app_router",
    "component_router",
    "edit_cell_router",
    "health_router",
    "page_router",
    "websocket_router",
]
