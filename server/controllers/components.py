from server.models.table import PgColumnDefinedProperty, PyColumnDefinedProperty, TableDefinedProperty
from server.models.widget import (
    ButtonDefinedProperty,
    InputDefinedProperty,
    SelectDefinedProperty,
    TextDefinedProperty,
    WidgetDefinedProperty,
)

component_property_types = {
    "table": TableDefinedProperty,
    "pycolumn": PyColumnDefinedProperty,
    "pgcolumn": PgColumnDefinedProperty,
    "widget": WidgetDefinedProperty,
    "input": InputDefinedProperty,
    "button": ButtonDefinedProperty,
    "text": TextDefinedProperty,
    "select": SelectDefinedProperty,
}


def get_component_properties(compnent_type: str):  # this needs to be modified to support mysql
    response = {}
    if compnent_type == "all":
        for key, value in component_property_types.items():
            response[key] = get_class_properties(value)
    else:
        response[compnent_type] = get_class_properties(component_property_types[compnent_type])
    return response


def get_class_properties(pydantic_model):
    model_schema = pydantic_model.schema()
    model_props = model_schema.get("properties")

    obj_props = []
    for key in model_props.keys():
        prop = model_props[key]
        prop["name"] = key

        if key in model_schema.get("required", []):
            prop["required"] = True

        if "description" in prop:
            prop["type"] = prop["description"]
            prop.pop("description")

        if "enum" in prop:
            prop["type"] = "select"
        obj_props.append(prop)

    return obj_props
