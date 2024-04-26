from pathlib import Path

import pandas as pd
from datamodel_code_generator import generate
from pydantic import Field, create_model

from dropbase.helpers.dataframe import to_dtable
from dropbase.helpers.display_rules import run_display_rule
from dropbase.helpers.utils import _dict_from_pydantic_model, get_empty_context, get_state_context_model
from dropbase.models.common import BaseContext, ColumnDisplayProperties, ComponentDisplayProperties
from dropbase.models.table import TableContextProperty
from dropbase.models.widget import SelectContextProperty, WidgetContextProperty, WidgetDefinedProperty

pd.DataFrame.to_dtable = to_dtable


def generate_context_model(properties):
    context = {}
    for key, value in properties:
        class_name = key.capitalize() + "Context"

        # create components contexts
        if isinstance(value, WidgetDefinedProperty):
            components_dir = {}
            for component in value.components:
                components_dir[component.name] = (component.context, ...)
            components_class_name = key.capitalize() + "ComponentsContext"
            components_class = create_model(components_class_name, **components_dir)

            locals()[class_name] = create_model(
                class_name,
                **{"components": (components_class, ...)},
                __base__=value.context,
            )
        else:
            # create table context model
            columns_dir = {}
            for column in value.columns:
                columns_dir[column.name] = (column.context, ...)
            columns_class_name = key.capitalize() + "ColumnsContext"
            columns_class = create_model(columns_class_name, **columns_dir)

            header_dir = {}
            for component in value.header:
                header_dir[component.name] = (component.context, ...)
            header_class_name = key.capitalize() + "HeaderContext"
            header_class = create_model(header_class_name, **header_dir)

            footer_dir = {}
            for component in value.footer:
                footer_dir[component.name] = (component.context, ...)
            footer_class_name = key.capitalize() + "FooterContext"
            footer_class = create_model(footer_class_name, **footer_dir)

            locals()[class_name] = create_model(
                class_name,
                **{
                    "columns": (columns_class, ...),
                    "header": (header_class, ...),
                    "footer": (footer_class, ...),
                },
                __base__=value.context,
            )

        # add each table context class into main context class
        context[key] = (locals()[class_name], ...)
    return create_model("Context", **context, __base__=BaseContext)


non_editable_components = ["button", "text"]


def compose_components_dir(components):
    components_dir = {}
    for component in components:
        # for widget_component in component.get("components"):
        # skip non-editable components, like text and button
        if component.component_type in non_editable_components:
            continue

        if component.component_type == "select" and component.multiple:
            component.data_type = "string_array"

        component_type = component_state_type_mapper(component.data_type)
        # state is pulled from ComponentDefined class
        components_dir[component.name] = (
            component_type,
            Field(default=None),
        )
    return components_dir


def compose_column_dir(columns):
    columns_dir = {}
    for column in columns:
        if column.column_type == "button_column":
            continue
        # skip non-editable columns
        if not column.display_type:
            continue

        column_type = column_state_type_mapper(column.display_type)
        columns_dir[column.name] = (
            column_type,
            Field(default=None),
        )
    return columns_dir


def compose_state_model(properties):
    state = {}
    for key, value in properties:
        class_name = key.capitalize() + "State"
        if isinstance(value, WidgetDefinedProperty):
            # props["component"] = {}
            components_dir = compose_components_dir(value.components)
            components_class_name = key.capitalize() + "ComponentsState"
            components_class = create_model(components_class_name, **components_dir)
            locals()[class_name] = create_model(class_name, **{"components": (components_class, ...)})
        else:
            header_dir = compose_components_dir(value.header)
            header_class_name = key.capitalize() + "HeaderState"
            header_class = create_model(header_class_name, **header_dir)

            footer_dir = compose_components_dir(value.footer)
            footer_class_name = key.capitalize() + "FooterState"
            footer_class = create_model(footer_class_name, **footer_dir)

            columns_dir = compose_column_dir(value.columns)
            columns_class_name = key.capitalize() + "ColumnsState"
            columns_class = create_model(columns_class_name, **columns_dir)

            locals()[class_name] = create_model(
                class_name,
                **{
                    "columns": (columns_class, ...),
                    "header": (header_class, ...),
                    "footer": (footer_class, ...),
                },
            )
        state[key] = (locals()[class_name], ...)
    return create_model("State", **state)


def compose_state_context_models(app_name: str, page_name: str, properties):

    page_dir_path = f"workspace/{app_name}/{page_name}"

    Context = generate_context_model(properties)
    State = compose_state_model(properties)
    generate(
        input_=Context.schema_json(indent=2),
        input_file_type="json",
        output=Path(page_dir_path + "/context.py"),
    )

    generate(
        input_=State.schema_json(indent=2),
        input_file_type="json",
        output=Path(page_dir_path + "/state.py"),
    )


def get_page_state_context(app_name: str, page_name: str, initial=False):
    State = get_state_context_model(app_name, page_name, "state")
    state = _dict_from_pydantic_model(State)
    if initial:
        context = get_empty_context(app_name, page_name).dict()
    else:
        context = run_display_rule(app_name, page_name, state)
    return {"state": state, "context": context}


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
