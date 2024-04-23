# schema boilerplates
schema_boilerplate_init = """from dropbase.helpers.pageABC import PageABC
from .scripts.main import *  # noqa, here we're importing all user defined classes


class Script(PageABC):
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
from typing import List
from dropbase.helpers.tableABC import TableABC
from dropbase.helpers.widgetABC import WidgetABC
from dropbase.schemas.edit_cell import CellEdit
from ..context import Context


class Table1(TableABC):

    def get_data(self) -> pd.DataFrame:
        # TODO: implement this method
        return pd.DataFrame()


class Widget1(WidgetABC):
    pass
"""
main_class = """
import pandas as pd
from ..base_class import ScriptBase
from ..context import Context


class Script(ScriptBase):{0}
"""
update_button_methods_main = "\n\ndef on_click_{0}(self) -> Context:\n    # TODO: implement this method\n    return self.context"  # noqa


table_class_boilerplate = """class {0}(TableABC):
    def get_data(self) -> pd.DataFrame:
        # Add your code here
        return pd.DataFrame()

    def update_row(self, edits: List[CellEdit) -> Context:
        # Add your code here
        return self.context
"""

widget_class_boilerplate = """class {0}(WidgetABC):
    pass
"""

# properties boilerplate
properties_boilerplate = """from dropbase.models import *
from .schema import Properties

table1 = TableDefinedProperty(label="Table 1", name="table1")
widget1 = WidgetDefinedProperty(label="Widget 1", name="widget1")
page = Properties(table1=table1, widget1=widget1)

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
        "columns": []
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
def get_data(self) -> pd.DataFrame:
    # Add your code here
    return pd.DataFrame()"""

update_row_template = """
def update_row(self, edits: List[CellEdit]) -> Context:
    # Add your code here
    return self.context"""
