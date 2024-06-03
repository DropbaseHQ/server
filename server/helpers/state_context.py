from pathlib import Path

import pandas as pd
from datamodel_code_generator import generate
from pydantic import Field, create_model

from dropbase.helpers.dataframe import to_dtable
from dropbase.helpers.display_rules import run_display_rule
from dropbase.helpers.utils import _dict_from_pydantic_model, get_empty_context, get_state_context_model
from dropbase.models.common import BaseContext
from dropbase.models.widget import WidgetProperty

pd.DataFrame.to_dtable = to_dtable


def generate_context_model(properties):
    context = {}
    for key, value in properties:
        class_name = key.capitalize() + "Context"

        # create components contexts
        if isinstance(value, WidgetProperty):
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
    table_update_classes = ""
    for key, value in properties:
        class_name = key.capitalize() + "State"
        if isinstance(value, WidgetProperty):
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

            # compose table update classes that will be used by table update method
            table_update_class_name = key.capitalize() + "ColumnUpdate"
            table_update_classes += f"""\n
class {table_update_class_name}(BaseModel):
    new: {columns_class_name}
    old: {columns_class_name}\n"""

        state[key] = (locals()[class_name], ...)
    return create_model("State", **state), table_update_classes


def compose_state_context_models(app_name: str, page_name: str, properties):

    page_dir_path = f"workspace/{app_name}/{page_name}"

    Context = generate_context_model(properties)
    generate(
        input_=Context.schema_json(indent=2),
        input_file_type="json",
        output=Path(page_dir_path + "/context.py"),
    )

    State, table_update_classes = compose_state_model(properties)
    generate(
        input_=State.schema_json(indent=2),
        input_file_type="json",
        output=Path(page_dir_path + "/state.py"),
    )
    # open state file and append table updates classes
    with open(Path(page_dir_path + "/state.py"), "a") as f:
        f.write(table_update_classes)


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
