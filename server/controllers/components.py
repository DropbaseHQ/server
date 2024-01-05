from server.controllers.utils import get_class_properties
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


def get_component_properties(compnent_type: str):
    response = {}
    if compnent_type == "all":
        for key, value in component_property_types.items():
            response[key] = get_class_properties(value)
    else:
        response[compnent_type] = get_class_properties(component_property_types[compnent_type])
    return response
