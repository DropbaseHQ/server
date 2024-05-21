from fastapi import APIRouter

from server.constants import DEFAULT_RESPONSES
from server.controllers.components import get_component_properties

router = APIRouter(prefix="/components", tags=["components"], responses=DEFAULT_RESPONSES)


@router.get("/properties/{component_type}")
def get_state_context_req(component_type: str):
    return get_component_properties(component_type)
