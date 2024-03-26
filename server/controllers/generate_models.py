from pathlib import Path

from datamodel_code_generator import generate
from pydantic import Field, create_model

from dropbase.models.table import TableContextProperty
from dropbase.models.table.button_column import ButtonColumnContextProperty
from dropbase.models.table.mysql_column import MySqlColumnContextProperty
from dropbase.models.table.pg_column import PgColumnContextProperty
from dropbase.models.table.py_column import PyColumnContextProperty
from dropbase.models.table.snowflake_column import SnowflakeColumnContextProperty
from dropbase.models.table.sqlite_column import SqliteColumnContextProperty
from dropbase.models.widget import (
    BooleanContextProperty,
    ButtonContextProperty,
    InputContextProperty,
    SelectContextProperty,
    TextContextProperty,
    WidgetContextProperty,
)


def column_state_type_mapper(state_type: str):
    match state_type:
        case "integer":
            return int
        case "float":
            return float
        case "boolean":
            return bool
        case "array":
            return list
        case _:
            return str


def component_state_type_mapper(input_type: str):
    match input_type:
        case "integer":
            return int
        case "float":
            return float
        case "boolean":
            return bool
        case "text":
            return str
        case "date":
            return str
        case "string_array":
            return list
        case _:
            return str


context_model_mapper = {
    "button": ButtonContextProperty,
    "boolean": BooleanContextProperty,
    "input": InputContextProperty,
    "select": SelectContextProperty,
    "text": TextContextProperty,
}


column_context_model_mapper = {
    "postgres": PgColumnContextProperty,
    "mysql": MySqlColumnContextProperty,
    "snowflake": SnowflakeColumnContextProperty,
    "sqlite": SqliteColumnContextProperty,
    "python": PyColumnContextProperty,
    "button_column": ButtonColumnContextProperty,
}


def compose_context_model(components):
    context = {}
    for name, item in components.items():
        class_name = name.capitalize() + "Context"
        props = {}

        # create components contexts
        if item["component_type"] == "widget":
            child = "components"
            base_model = WidgetContextProperty
            for component in item["components"]:
                component_type = component.get("component_type")
                BaseProperty = context_model_mapper.get(component_type)
                # create component context class
                props[component["name"]] = (BaseProperty, ...)

        else:
            child = "columns"
            base_model = TableContextProperty
            for column in item["columns"]:
                column_type = column.get("column_type")
                BaseProperty = column_context_model_mapper.get(column_type)
                # create column context class
                props[column["name"]] = (BaseProperty, ...)

        child_class_name = name.capitalize() + child.capitalize() + "Context"
        child_class = create_model(child_class_name, **props)

        # create table context class
        locals()[class_name] = create_model(
            class_name,
            **{child: (child_class, ...)},
            __base__=base_model,
        )

        # add each table context class into main context class
        context[name] = (locals()[class_name], ...)
    return create_model("Context", **context)


def compose_state_model(components):
    state = {}
    non_editable_components = ["button", "text"]
    for name, item in components.items():
        props = {}
        if item["component_type"] == "widget":
            for component in item.get("components"):
                # skip non-editable components, like text and button
                if component["component_type"] in non_editable_components:
                    continue

                if component.get("component_type") == "select" and component.get("multiple"):
                    component["data_type"] = "string_array"

                component_type = component_state_type_mapper(component.get("data_type"))
                # state is pulled from ComponentDefined class
                props[component["name"]] = (
                    component_type,
                    Field(default=None),
                )
        else:
            for column in item.get("columns"):
                # skip non-editable columns
                if not column.get("display_type"):
                    continue

                column_type = column_state_type_mapper(column.get("display_type"))
                # state is pulled from ComponentDefined class
                props[column["name"]] = (
                    column_type,
                    Field(default=None),
                )

        class_name = name.capitalize() + "State"
        locals()[class_name] = create_model(class_name, **props)
        state[name] = (locals()[class_name], ...)

    # compose State
    return create_model("State", **state)


def create_state_context_files(output_path: str, properties: dict):
    # context
    context = compose_context_model(properties["components"])
    generate(
        input_=context.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/context.py"),
    )
    # state
    state = compose_state_model(properties["components"])
    generate(
        input_=state.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/state.py"),
    )
