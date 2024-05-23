# schema boilerplates
sctipt_boilerplate_init = """from dropbase.helpers.scriptABC import ScriptABC
from .scripts.main import *  # noqa, here we're importing all user defined classes


class Script(ScriptABC):
    def __init__(self, app_name, page_name):
        super().__init__(app_name, page_name)
        kwards = {"app_name": self.app_name, "page_name": self.page_name}
        for key, _ in self.properties:
            class_name = key.capitalize()
            class_ = globals()[class_name]  # Get the actual class name from globals
            self.__dict__[key] = class_(**kwards, name=key)
"""
# create
schema_boilerplate = """from pydantic import BaseModel

from dropbase.models.table import TableProperty
from dropbase.models.widget import WidgetProperty


class Properties(BaseModel):
    table1: TableProperty
    widget1: WidgetProperty
"""


# main boilerplates
# create
main_class_init = """import pandas as pd
from typing import List
from dropbase.helpers.tableABC import TableABC
from dropbase.helpers.widgetABC import WidgetABC
from workspace.{0}.{1}.context import *
from workspace.{0}.{1}.state import *


class Table1(TableABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        # Add your code here
        table_data = pd.DataFrame()
        context.table1.data = table_data.to_dtable()
        return context

    def add(self, state: State, context: Context, row: Table1ColumnsState) -> Context:
        return context

    def update(self, state: State, context: Context, updates: List[Table1ColumnUpdate]) -> Context:
        return context

    def delete(self, state: State, context: Context) -> Context:
        return context

    def on_row_change(self, state: State, context: Context) -> Context:
        return context

class Widget1(WidgetABC):
    pass
"""

update_button_methods_main = """

def {0}(self, state: State, context: Context) -> Context:
    # TODO: implement this method
    return context
"""


table_class_boilerplate = """class {0}(TableABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        # Add your code here
        table_data = pd.DataFrame()
        context.{1}.data = table_data.to_dtable()
        return context

    def add(self, state: State, context: Context, row: {0}ColumnsState) -> Context:
        return context

    def update(self, state: State, context: Context, updates: List[{0}ColumnUpdate]) -> Context:
        return context

    def delete(self, state: State, context: Context) -> Context:
        return context

    def on_row_change(self, state: State, context: Context) -> Context:
        return context
"""

widget_class_boilerplate = """class {0}(WidgetABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
"""


# workspace boilerplate
app_init_boilerplate = """
import importlib
import os
import pkgutil

# import immediate subdirectories, should only import widgets
for importer, modname, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)]):
    module_dir = os.path.join(os.path.dirname(__file__), modname)
    if ispkg and os.path.exists(module_dir):
        importlib.import_module(f".{modname}", __package__)
"""


page_init_boilerplate = """from workspace.{0}.{1}.context import *
from workspace.{0}.{1}.state import *
"""


properties_json_boilerplate = """{
    "table1":{
        "name":"table1",
        "label":"Table 1",
        "block_type": "table",
        "columns": [],
        "header": [],
        "footer": [],
        "w": 4,
        "h": 1,
        "x": 0,
        "y": 0
    },
    "widget1": {
        "name": "widget1",
        "label": "Widget 1",
        "block_type": "widget",
        "components": []
    }
}"""


app_properties_boilerplate = {
    "page1": {
        "label": "Page1",
    }
}


table_method_templates = {
    "get": """
def get(self, state: State, context: Context):
    # Add your code here
    return context""",
    "add": """
def add(self, state, context, row: dict) -> Context:
    return context""",
    "update": """
def update(self, state, context, row: dict) -> Context:
    return context""",
    "delete": """
def delete(self, state, context, row: dict) -> Context:
    return context""",
    "on_row_change": """
def on_row_change(self, state, context) -> Context:
    return context""",
}

get_data_template = """
def get(self, state: State, context: Context):
    # Add your code here
    return context"""

add_data_template = """
def add(self, state, context, row: dict) -> Context:
    return context"""

update_data_template = """
def update(self, state, context, row: dict) -> Context:
    return context"""

delete_data_template = """
def delete(self, state, context, row: dict) -> Context:
    return context"""

on_row_change_template = """
def on_row_change(self, state, context) -> Context:
    return context"""
