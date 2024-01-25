import sqlalchemy.exc
from fastapi import APIRouter, HTTPException, Depends

from server.controllers.query import run_query
from server.schemas.run_python import QueryPythonRequest
from server.auth.dependency import EnforceUserAppPermissions

router = APIRouter(
    prefix="/query", tags=["query"], responses={404: {"description": "Not found"}}
)


@router.post("/", dependencies=[Depends(EnforceUserAppPermissions(action="use"))])
async def run_query_req(req: QueryPythonRequest):
    try:
        return run_query(req)
    except sqlalchemy.exc.ProgrammingError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))
