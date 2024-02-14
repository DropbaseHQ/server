import operator
from functools import reduce

from dropbase.models.table import (
    ButtonColumnDefinedProperty,
    PgColumnDefinedProperty,
    PyColumnDefinedProperty,
    TableDefinedProperty,
)
from dropbase.models.widget import (
    BooleanDefinedProperty,
    ButtonDefinedProperty,
    InputDefinedProperty,
    SelectDefinedProperty,
    TextDefinedProperty,
    WidgetDefinedProperty,
)

component_property_types = {
    "table": TableDefinedProperty,
    "button_column": ButtonColumnDefinedProperty,
    "pycolumn": PyColumnDefinedProperty,
    "pgcolumn": PgColumnDefinedProperty,
    "widget": WidgetDefinedProperty,
    "input": InputDefinedProperty,
    "button": ButtonDefinedProperty,
    "text": TextDefinedProperty,
    "select": SelectDefinedProperty,
    "boolean": BooleanDefinedProperty,
}


def get_component_properties(compnent_type: str):
    response = {}
    if compnent_type == "all":
        for key, value in component_property_types.items():
            response[key] = get_class_properties(value)
    else:
        response[compnent_type] = get_class_properties(component_property_types[compnent_type])
    return response


def reduce_method(a, b):
    return reduce(operator.getitem, a, b)


def parse_prop(prop, key, model_schema):

    if "anyOf" in prop:
        prop["type"] = []
        for each_prop in prop["anyOf"]:
            prop["type"].append(parse_prop(each_prop, key, model_schema))
        prop.pop("anyOf")
    if "$ref" in prop:
        path = prop["$ref"][2:].split("/")
        prop = reduce_method(path, model_schema)

    if key in model_schema.get("required", []):
        prop["required"] = True

    if "description" in prop:
        prop["type"] = prop["description"]
        prop.pop("description")

    if "enum" in prop:
        prop["type"] = "select"

    prop["name"] = key
    return prop


def get_class_properties(pydantic_model):
    model_schema = pydantic_model.schema()
    model_props = model_schema.get("properties")

    obj_props = []
    for key in model_props.keys():
        prop = model_props[key]
        prop = parse_prop(prop, key, model_schema)
        obj_props.append(prop)

    return obj_props
