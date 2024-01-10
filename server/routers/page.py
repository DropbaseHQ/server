from fastapi import APIRouter, Response

from server.controllers.page import get_page_state_context, update_page_properties
from server.controllers.utils import read_page_properties
from server.schemas.page import PageProperties

router = APIRouter(prefix="/page", tags=["page"], responses={404: {"description": "Not found"}})


@router.get("/{app_name}/{page_name}")
def get_state_context_req(app_name: str, page_name: str):
    state_context = get_page_state_context(app_name, page_name)
    state_context["properties"] = read_page_properties(app_name, page_name)
    return state_context


@router.post("/")
def cud_page_props(
    req: PageProperties,
    response: Response,
):
    try:
        # update local json file
        return update_page_properties(req)
    except Exception as e:
        # TODO: delete files if error
        response.status_code = 500
        return {"error": str(e)}
