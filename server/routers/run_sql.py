from fastapi import APIRouter, Response

from server.schemas.query import RunSQLRequest
from server.controllers.query import run_df_query, verify_state

router = APIRouter(prefix="/run_sql", tags=["run_sql"], responses={404: {"description": "Not found"}})


@router.post("/run_sql_string/")
async def run_sql_from_string_req(req: RunSQLRequest, response: Response):
    try:
        resp, status_code = verify_state(req.app_name, req.page_name, req.state)
        if status_code != 200:
            response.status_code = status_code
            return resp

        df = run_df_query(req.file_content, req.source, req.state)
        result = {"columns": df.columns.tolist(), "data": df.values.tolist()}
        return {"success": True, "result": result, "stdout": ""}
    except Exception as e:
        return {"success": False, "result": str(e), "stdout": ""}
