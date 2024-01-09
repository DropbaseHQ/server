import json

from pydantic import BaseModel

from server.constants import cwd
from server.controllers.utils import get_state_context_model, read_page_properties
from server.controllers.display_rules import run_display_rule


def update_page_props(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        f.write(json.dumps(properties, indent=2))


def get_page_props(app_name: str, page_name: str):
    return read_page_properties(app_name, page_name)


def get_page_state_context(app_name: str, page_name: str):
    State = get_state_context_model(app_name, page_name, "state")
    Context = get_state_context_model(app_name, page_name, "context")
    state = _dict_from_pydantic_model(State)
    context = _dict_from_pydantic_model(Context)
    new_context = run_display_rule(app_name, page_name, state, context)
    return {"state": state, "context": new_context}


def _dict_from_pydantic_model(model):
    data = {}
    for name, field in model.__fields__.items():
        if isinstance(field.outer_type_, type) and issubclass(
            field.outer_type_, BaseModel
        ):
            data[name] = _dict_from_pydantic_model(field.outer_type_)
        else:
            data[name] = field.default
    return data
