from fastapi import APIRouter, Response

from server.schemas.run_python import QueryPythonRequest
from server.controllers.query import run_python_query, run_sql_query

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest, response: Response):    
    if req.file.type == "data_fetcher":
        resp, status_code = run_python_query(
            app_name=req.app_name,
            page_name=req.page_name,
            file=req.file,
            state=req.state,
            filter_sort=req.filter_sort,
        )
    else:
        resp, status_code = run_sql_query(
            app_name=req.app_name,
            page_name=req.page_name,
            file=req.file,
            state=req.state,
            filter_sort=req.filter_sort,
        )

    response.status_code = status_code
    return resp
