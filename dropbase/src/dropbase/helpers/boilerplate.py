# schema boilerplates
schema_boilerplate_init = """from dropbase.helpers.pageABC import PageABC
from .scripts.main import *  # noqa, here we're importing all user defined classes


class Page(PageABC):
    def __init__(self, app_name, page_name, state):
        super().__init__(app_name, page_name, state)
        kwards = {
            "app_name": self.app_name,
            "page_name": self.page_name,
            "state": self.state,
            "context": self.context,
        }
        for key, _ in self.properties:
            class_name = key.capitalize()
            class_ = globals()[class_name]  # Get the actual class name from globals
            self.__dict__[key] = class_(**kwards, name=key)
"""
# create
schema_boilerplate = """from pydantic import BaseModel

from dropbase.models.table import TableDefinedProperty
from dropbase.models.widget import WidgetDefinedProperty


class Properties(BaseModel):
    table1: TableDefinedProperty
    widget1: WidgetDefinedProperty
"""


# main boilerplates
# create
main_class_init = """import pandas as pd
from dropbase.helpers.tableABC import TableABC
from dropbase.helpers.widgetABC import WidgetABC
from ..context import Context
from ..state import State


class Table1(TableABC):

    def get_data(self, state: State, context: Context) ->pd.DataFrame:
        # TODO: implement this method
        return pd.DataFrame()

    def get(self, state: State, context: Context):
        context.table1.data = self.get_data(state, context).to_dtable()
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
    def get_data(self, state: State, context: Context) -> pd.DataFrame:
        # Add your code here
        return pd.DataFrame()

    def get(self, state: State, context: Context):
        context.{1}.data = self.get_data(state, context).to_dtable()
        return context
"""

widget_class_boilerplate = """class {0}(WidgetABC):
    pass
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


page_init_boilerplate = """from .context import Context
from .state import State
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

get_data_template = """
def get_data(self, state: State, context: Context) -> pd.DataFrame:
    # Add your code here
    return pd.DataFrame()"""
