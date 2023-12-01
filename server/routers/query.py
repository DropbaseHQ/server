import sqlalchemy.exc
from fastapi import APIRouter, HTTPException

from server.schemas.run_python import QueryPythonRequest
from server.controllers.query import run_sql_query, run_python_query

router = APIRouter(prefix="/query", tags=["query"], responses={404: {"description": "Not found"}})


@router.post("/")
async def run_query(req: QueryPythonRequest):
    try:
        if req.file.type == "data_fetcher":
            resp = run_python_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
        else:
            resp = run_sql_query(req.app_name, req.page_name, req.file, req.state, req.filter_sort)
        return resp
    except sqlalchemy.exc.ProgrammingError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))