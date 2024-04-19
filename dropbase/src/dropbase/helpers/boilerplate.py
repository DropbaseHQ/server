# base class boilerplates

table_methods_base = """
    @abstractmethod
    def get_{0}(self) -> pd.DataFrame:
        pass

    def update_{0}(self) -> Context:
        pass

    def delete_{0}(self) -> Context:
        pass
"""
button_methods_base = """
    @abstractmethod
    def on_click_{0}(self) -> Context:
        pass
"""

input_methods_base = """
    @abstractmethod
    def on_enter_{0}(self) -> Context:
        pass
"""

base_class = """
from abc import abstractmethod
import pandas as pd
from dropbase.helpers.pageABC import PageABC
from .context import Context


class PageBase(PageABC):
{0}"""


# schema boilerplates
# create
schema_boilerplate = """from pydantic import BaseModel

from dropbase.models.table import TableDefinedProperty
from dropbase.models.widget import WidgetDefinedProperty


class PageProperties(BaseModel):
    table1: TableDefinedProperty
    widget1: WidgetDefinedProperty

"""
# update
schema_boilerplate_create = """from pydantic import BaseModel

from dropbase.models.table import TableDefinedProperty
from dropbase.models.widget import WidgetDefinedProperty


class PageProperties(BaseModel):
"""


# main boilerplates
# create
main_class = """
import pandas as pd
from ..base_class import PageBase
from ..context import Context


class Page(PageBase):
{0}
"""
table_methods_main = "    def get_{0}(self) -> pd.DataFrame:\n        # TODO: implement this method\n        return pd.DataFrame()\n\n"
button_methods_main = "    def on_click_{0}(self) -> Context:\n        # TODO: implement this method\n        return self.context\n\n"
input_methods_main = "    def on_enter_{0}(self) -> Context:\n        # TODO: implement this method\n        return self.context\n\n"

# update
update_table_methods_main = "def get_{0}(self) -> pd.DataFrame:\n    # TODO: implement this method\n    return pd.DataFrame()\n\n"
update_button_methods_main = (
    "def on_click_{0}(self) -> Context:\n    # TODO: implement this method\n    return self.context\n\n"
)
update_input_methods_main = (
    "def on_enter_{0}(self) -> Context:\n    # TODO: implement this method\n    return self.context\n\n"
)


# properties boilerplate
properties_boilerplate = """from dropbase.models import *
from .schema import PageProperties

table1 = TableDefinedProperty(label="Table 1", name="table1")
widget1 = WidgetDefinedProperty(label="Widget 1", name="widget1")
page = PageProperties(table1=table1, widget1=widget1)

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
        "label":"Table 1"
    },
    "widget1": {
        "name": "widget1",
        "label": "Widget 1"
    }
}"""
