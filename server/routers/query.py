from fastapi import APIRouter

from server.controllers.query import run_sql_query, run_python_query
from server.schemas.run_python import QueryPythonRequest

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest):
    if req.file.type == "data_fetcher":
        resp = run_python_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
    else:
        resp = run_sql_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
    return resp
