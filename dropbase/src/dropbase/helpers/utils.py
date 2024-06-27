import importlib
import json

from pydantic import BaseModel, create_model

from dropbase.models.charts import ChartProperty
from dropbase.models.table import TableProperty
from dropbase.models.widget import WidgetProperty


def get_state(app_name: str, page_name: str, state: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    importlib.reload(page)
    State = getattr(page, "State")
    return State(**state)


def get_state_context_model(app_name: str, page_name: str, model_type: str):
    module_name = f"workspace.{app_name}.{page_name}.{model_type}"
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    return getattr(module, model_type.capitalize())


def read_page_properties(app_name: str, page_name: str):
    path = f"workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def read_app_properties(app_name: str):
    path = f"workspace/{app_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def compose_properties_schema(properties: dict):
    block_type_mapping = {"table": TableProperty, "widget": WidgetProperty, "chart": ChartProperty}

    # compose fields for pydantic model
    fields = {}
    for key, value in properties.items():
        block_type = value["block_type"]
        fields[key] = (block_type_mapping[block_type], ...)

    return create_model("Properties", **fields)


def get_page_properties(app_name: str, page_name: str):
    properties = read_page_properties(app_name, page_name)
    Properties = compose_properties_schema(properties)
    # create page object
    return Properties(**properties)


def validate_page_properties(properties: dict):
    for key, value in properties.items():
        if key != value["name"]:
            raise ValueError(f"Key {key} does not match name {value['name']}")
    Properties = compose_properties_schema(properties)
    return Properties(**properties)


def _dict_from_pydantic_model(model):
    data = {}
    for name, field in model.__fields__.items():
        if isinstance(field.outer_type_, type) and issubclass(field.outer_type_, BaseModel):
            data[name] = _dict_from_pydantic_model(field.outer_type_)
        else:
            data[name] = field.default
    return data


def get_empty_context(app_name: str, page_name: str):
    Context = get_state_context_model(app_name, page_name, "context")
    context = _dict_from_pydantic_model(Context)
    return Context(**context)


def get_state_empty_context(app_name: str, page_name: str, state: dict):
    State = get_state_context_model(app_name, page_name, "state")
    Context = get_state_context_model(app_name, page_name, "context")
    context = _dict_from_pydantic_model(Context)

    return State(**state), Context(**context)
