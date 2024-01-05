import importlib
import json

from pydantic import BaseModel

from server.constants import cwd


def update_page_props(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        f.write(json.dumps(properties))


def get_page_props(app_name: str, page_name: str):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def get_page_state_context(app_name: str, page_name: str):
    state_module_name = f"workspace.{app_name}.{page_name}.state"
    context_module_name = f"workspace.{app_name}.{page_name}.context"
    state_module = importlib.import_module(state_module_name)
    context_module = importlib.import_module(context_module_name)
    # TODO: confirm we need to reload modules
    state_module = importlib.reload(state_module)
    context_module = importlib.reload(context_module)
    State = getattr(state_module, "State")
    Context = getattr(context_module, "Context")
    state = _dict_from_pydantic_model(State)
    context = _dict_from_pydantic_model(Context)
    return {"state": state, "context": context}


def _dict_from_pydantic_model(model):
    data = {}
    for name, field in model.__fields__.items():
        if isinstance(field.outer_type_, type) and issubclass(field.outer_type_, BaseModel):
            data[name] = _dict_from_pydantic_model(field.outer_type_)
        else:
            data[name] = field.default
    return data
