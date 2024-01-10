# state
from pathlib import Path

from datamodel_code_generator import generate
from pydantic import BaseModel, Field, create_model

from server.models import (
    ButtonContextProperty,
    ButtonDefinedProperty,
    InputContextProperty,
    InputDefinedProperty,
    PgColumnContextProperty,
    PgColumnDefinedProperty,
    PyColumnContextProperty,
    PyColumnDefinedProperty,
    SelectContextProperty,
    SelectDefinedProperty,
    TableContextProperty,
    TextContextProperty,
    TextDefinedProperty,
    WidgetContextProperty,
)

component_name_to_models = {
    "button": ButtonDefinedProperty,
    "input": InputDefinedProperty,
    "select": SelectDefinedProperty,
    "text": TextDefinedProperty,
    "py": PyColumnDefinedProperty,
    "pg": PgColumnDefinedProperty,
}


def column_state_type_mapper(state_type: str):
    match state_type:
        case "integer":
            return int
        case "float":
            return float
        case "boolean":
            return bool
        case _:
            return str


def component_state_type_mapper(input_type: str):
    match input_type:
        case "integer":
            return int
        case "float":
            return float
        case "bool":
            return bool
        case "text":
            return str
        case "date":
            return str
        case _:
            return str


def get_widget_state_class(widgets_props):
    non_editable = ["button", "text"]
    widgets_state = {}

    for widget_data in widgets_props:
        widget_name = widget_data.get("name")
        widget_components = widget_data.get("components")
        components_props = {}
        for component in widget_components:
            # skip non-editable components, like text and button
            if component["component_type"] in non_editable:
                continue

            # get the type that will be used in state. this is what client will send back to server
            component_name = component["name"]
            component_type = component_state_type_mapper(component.get("data_type"))

            # state is pulled from ComponentDefined class
            components_props[component_name] = (
                component_type,
                Field(default=None),
            )

        widget_class_name = widget_name.capitalize() + "State"
        locals()[widget_class_name] = create_model(widget_class_name, **components_props)

        widgets_state[widget_name] = (locals()[widget_class_name], ...)

    # compose Widgets
    return create_model("WidgetsState", **widgets_state)


def get_tables_state_class(tables_props):
    tables_state = {}

    for table_data in tables_props:
        table_name = table_data.get("name")
        table_columns = table_data.get("columns")

        columns_props = {}
        for column in table_columns:

            column_name = column["name"]
            column_type = column_state_type_mapper(column.get("display_type"))

            # state is pulled from ComponentDefined class
            columns_props[column_name] = (
                column_type,
                Field(default=None),
            )

        table_class_name = table_name.capitalize() + "State"
        locals()[table_class_name] = create_model(table_class_name, **columns_props)

        tables_state[table_name] = (locals()[table_class_name], ...)

    # compose Widgets
    return create_model("TablesState", **tables_state)


def create_state(component_props):
    WidgetState = get_widget_state_class(component_props.get("widgets"))
    TablesState = get_tables_state_class(component_props.get("tables"))

    class State(BaseModel):
        widgets: WidgetState
        tables: TablesState

    return State


context_model_mapper = {
    "button": ButtonContextProperty,
    "input": InputContextProperty,
    "select": SelectContextProperty,
    "text": TextContextProperty,
    "sql": PgColumnContextProperty,
    "python": PyColumnContextProperty,
}


def get_widget_context(widgets_props):
    widgets_context = {}
    for widget_data in widgets_props:

        widget_name = widget_data.get("name")
        widget_components = widget_data.get("components")

        # create components contexts
        components_props = {}
        for component in widget_components:

            component_type = component.get("component_type")
            BaseProperty = context_model_mapper.get(component_type)
            # create component context class
            components_props[component["name"]] = (BaseProperty, ...)

        components_class_name = widget_name.capitalize() + "ComponentsContext"
        widget_components_class = create_model(components_class_name, **components_props)

        widget_class_name = widget_name.capitalize() + "Context"

        # create widget context class
        locals()[widget_class_name] = create_model(
            widget_class_name,
            **{"components": (widget_components_class, ...)},
            __base__=WidgetContextProperty,
        )

        # add each widget context class into main context class
        widgets_context[widget_name] = (locals()[widget_class_name], ...)
    return create_model("WidgetsContext", **widgets_context)


def get_table_context(tables_props):
    tables_context = {}
    for table_data in tables_props:

        table_name = table_data.get("name")
        table_columns = table_data.get("columns")

        # create columns contexts
        columns_props = {}
        for column in table_columns:

            column_type = table_data.get("type")
            # column.get("column_type")

            BaseProperty = context_model_mapper.get(column_type)
            # create column context class
            columns_props[column["name"]] = (BaseProperty, ...)

        columns_class_name = table_name.capitalize() + "ColumnsContext"
        table_columns_class = create_model(columns_class_name, **columns_props)

        table_class_name = table_name.capitalize() + "Context"

        # create table context class
        locals()[table_class_name] = create_model(
            table_class_name, **{"columns": (table_columns_class, ...)}, __base__=TableContextProperty
        )

        # add each table context class into main context class
        tables_context[table_name] = (locals()[table_class_name], ...)
    return create_model("TablessContext", **tables_context)


def create_context(component_props):
    WidgetState = get_widget_context(component_props.get("widgets"))
    TablesState = get_table_context(component_props.get("tables"))

    class Context(BaseModel):
        widgets: WidgetState
        tables: TablesState

    return Context


def create_state_context_files(app_name: str, page_name: str, properties: dict):
    output_path = f"workspace/{app_name}/{page_name}"
    # context
    context = create_context(properties)
    generate(
        input_=context.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/context.py"),
    )
    # state
    state = create_state(properties)
    generate(
        input_=state.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/state.py"),
    )
