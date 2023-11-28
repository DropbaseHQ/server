from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routers import (
    app_router,
    component_router,
    edit_cell_router,
    files_router,
    function_router,
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
origins = [
    "http://localhost:3030",
    "http://www.localhost:3030",
    "https://app.dropbase.io",
    "https://www.app.dropbase.io",
]

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
