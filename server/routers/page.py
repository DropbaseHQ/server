from fastapi import APIRouter, Response

from server.controllers.generate_models import create_state_context_files
from server.controllers.page import get_page_state_context, update_comp_props
from server.schemas.page import PageProperties

router = APIRouter(prefix="/page", tags=["page"], responses={404: {"description": "Not found"}})


@router.post("/")
def update_page_props(
    req: PageProperties,
    response: Response,
):
    try:
        # update local json file
        update_comp_props(**req.dict())
        # update state context
        create_state_context_files(**req.dict())
        # get new steate and context
        return get_page_state_context(req.app_name, req.page_name)
    except Exception as e:
        # TODO: delete files if error
        response.status_code = 500
        return {"error": str(e)}
