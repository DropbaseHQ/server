# TODO: delete, being replaced by state_context in dropbase package
from pathlib import Path

from datamodel_code_generator import generate
from pydantic import Field, create_model

from dropbase.models.common import BaseContext, ColumnDisplayProperties, ComponentDisplayProperties
from dropbase.models.table import TableContextProperty
from dropbase.models.widget import SelectContextProperty, WidgetContextProperty


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


def compose_context_model(components):
    context = {}
    for component in components:
        name = component["name"]
        class_name = name.capitalize() + "Context"
        props = {}

        # create components contexts
        if component["block_type"] == "widget":
            child = "components"
            base_model = WidgetContextProperty
            for widget_component in component["components"]:
                component_type = widget_component.get("component_type")
                if component_type == "select":
                    BaseProperty = SelectContextProperty
                else:
                    BaseProperty = ComponentDisplayProperties
                # create component context class
                props[widget_component["name"]] = (BaseProperty, ...)

        else:
            child = "columns"
            base_model = TableContextProperty
            for column in component["columns"]:
                BaseProperty = ColumnDisplayProperties
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
    return create_model("Context", **context, __base__=BaseContext)


def compose_state_model(components):
    state = {}
    non_editable_components = ["button", "text"]
    for component in components:
        name = component["name"]
        props = {}
        if component["block_type"] == "widget":
            for widget_component in component.get("components"):
                # skip non-editable components, like text and button
                if widget_component["component_type"] in non_editable_components:
                    continue

                if widget_component.get("component_type") == "select" and widget_component.get(
                    "multiple"
                ):  # noqa
                    widget_component["data_type"] = "string_array"

                component_type = component_state_type_mapper(widget_component.get("data_type"))
                # state is pulled from ComponentDefined class
                props[widget_component["name"]] = (
                    component_type,
                    Field(default=None),
                )
        else:
            for column in component.get("columns"):
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
    context = compose_context_model(properties["blocks"])
    generate(
        input_=context.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/context.py"),
    )
    # state
    state = compose_state_model(properties["blocks"])
    generate(
        input_=state.schema_json(indent=2),
        input_file_type="json",
        output=Path(output_path + "/state.py"),
    )
