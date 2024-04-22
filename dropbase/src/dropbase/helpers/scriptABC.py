import importlib
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd
from datamodel_code_generator import generate
from pydantic import Field, create_model

from dropbase.helpers.dataframe import to_dtable
from dropbase.helpers.utils import _dict_from_pydantic_model, get_page_properties
from dropbase.models.common import BaseContext
from dropbase.models.table import TableDefinedProperty
from dropbase.models.widget import WidgetDefinedProperty
from dropbase.schemas.edit_cell import CellEdit

pd.DataFrame.to_dtable = to_dtable


class WidgetBase(ABC):
    def __init__(self):
        self.app_name = self.app_name
        self.page_name = self.page_name
        self.state = self.state
        self.context = self.context


class TableBase(ABC):
    def __init__(self):
        self.app_name = self.app_name
        self.page_name = self.page_name
        self.state = self.state
        self.context = self.context

    @abstractmethod
    def get_data(self):
        pass

    def udpate_row(self, edits: list[CellEdit]):
        pass

    def create_row(self, row: dict):
        pass

    def delete_row(self, row: dict):
        pass

    def handle_updates(self, updates: list):
        for update in updates:
            self.update_row(update)
        return self.context


class ScriptABC(ABC):
    """
    handles user script execution, running functions
    """

    def __init__(self, app_name: str, page_name: str, state: dict):

        # load state and context
        page_path = f"workspace.{app_name}.{page_name}"
        state_context_module = importlib.import_module(page_path)
        importlib.reload(state_context_module)
        # init state
        State = getattr(state_context_module, "State")
        state = State(**state)
        # init context
        Context = getattr(state_context_module, "Context")
        context = _dict_from_pydantic_model(Context)
        context = Context(**context)

        # set properties
        self.properties = get_page_properties(app_name, page_name)

        # set state and context
        self.app_name = app_name
        self.page_name = page_name
        self.state = state
        self.context = context

    def reload_properties(self):
        properties = get_page_properties(self.app_name, self.page_name)
        self.properties = properties
        return self.properties

    # generic methods used by dropbase
    def get_table_data(self, table_name: str):
        self.context.__getattribute__(table_name).data = getattr(self, f"get_{table_name}")().to_dtable()
        return self.context

    def load_page(self):
        # todo: get tables from context
        tables = self.get_table_names()
        for table in tables:
            self.get_table_data(table)
        return self.context

    def get_table_names(self):
        tables = []
        for key, values in self.properties:
            if isinstance(values, TableDefinedProperty):
                tables.append(key)
        return tables


# TODO: move to utils
data_type_column_mapper = {"python": "PyColumnDefinedProperty"}


def generate_context_model(properties):
    context = {}
    for key, value in properties:
        class_name = key.capitalize() + "Context"
        props = {}

        # create components contexts
        if isinstance(value, WidgetDefinedProperty):
            child = "components"
            for component in value.components:
                props[component.name] = (component.context, ...)
        else:
            child = "columns"
            for column in value.columns:
                props[column.name] = (column.context, ...)

        child_class_name = key.capitalize() + child.capitalize() + "Context"
        child_class = create_model(child_class_name, **props)

        # create table context class
        locals()[class_name] = create_model(
            class_name,
            **{child: (child_class, ...)},
            __base__=value.context,
        )

        # add each table context class into main context class
        context[key] = (locals()[class_name], ...)
    return create_model("Context", **context, __base__=BaseContext)


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


def compose_state_model(properties):
    state = {}
    non_editable_components = ["button", "text"]
    for key, value in properties:
        class_name = key.capitalize() + "State"
        props = {}
        if isinstance(value, WidgetDefinedProperty):
            for component in value.components:
                # for widget_component in component.get("components"):
                # skip non-editable components, like text and button
                if component.component_type in non_editable_components:
                    continue

                if component.component_type == "select" and component.multiple:
                    component.data_type = "string_array"

                component_type = component_state_type_mapper(component.data_type)
                # state is pulled from ComponentDefined class
                props[component.name] = (
                    component_type,
                    Field(default=None),
                )
        else:
            for column in value.columns:
                # skip non-editable columns
                if not column.display_type:
                    continue

                column_type = column_state_type_mapper(column.display_type)
                # state is pulled from ComponentDefined class
                props[column.name] = (
                    column_type,
                    Field(default=None),
                )

        locals()[class_name] = create_model(class_name, **props)
        state[key] = (locals()[class_name], ...)

    # compose State
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
