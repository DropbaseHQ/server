from fastapi import APIRouter, HTTPException

from server.constants import DEFAULT_RESPONSES
from server.controllers.components import get_component_properties

router = APIRouter(prefix="/components", tags=["components"], responses=DEFAULT_RESPONSES)


@router.get("/properties/{component_type}")
def get_state_context_req(component_type: str):
    try:
        return get_component_properties(component_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
