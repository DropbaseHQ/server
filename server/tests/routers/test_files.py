import importlib
import json


def test_update_main_file(client):

    app_name, page_name, file_name = "pages", "page4", "main.py"
    payload = {
        "app_name": app_name,
        "page_name": page_name,
        "file_name": file_name,
        "code": update_main_file_code,
    }
    response = client.put("/files/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"File {file_name} updated successfully"}

    # check if main.py has been updated
    file_path = f"workspace/{app_name}/{page_name}/{file_name}"
    with open(file_path, "r") as f:
        assert f.read() == update_main_file_code


def test_update_properties_file(client):
    app_name, page_name, file_name = "pages", "page4", "properties.json"
    payload = {
        "app_name": app_name,
        "page_name": page_name,
        "file_name": file_name,
        "code": update_propreties_file_code,
    }
    response = client.put("/files/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"File {file_name} updated successfully"}

    # check if properties.json has been updated
    file_path = f"workspace/{app_name}/{page_name}/{file_name}"
    with open(file_path, "r") as f:
        saved_properties = json.loads(f.read())
    # NOTE: compare as dict because json.loads will convert to dict
    json.loads(update_propreties_file_code) == saved_properties

    # check if state has been updated
    state_module = importlib.import_module(f"workspace.{app_name}.{page_name}.state")
    importlib.reload(state_module)
    Widget1ComponentsState = getattr(state_module, "Widget1ComponentsState", None)
    assert Widget1ComponentsState is not None
    assert "input1" in Widget1ComponentsState.__annotations__
    assert Widget1ComponentsState.__annotations__["input1"] == "Optional[str]"

    # check if context has been updated
    context_module = importlib.import_module(f"workspace.{app_name}.{page_name}.context")
    importlib.reload(context_module)
    Widget1ComponentsContext = getattr(context_module, "Widget1ComponentsContext", None)
    assert Widget1ComponentsContext is not None
    assert "input1" in Widget1ComponentsContext.__annotations__
    assert Widget1ComponentsContext.__annotations__["input1"] == "ComponentProperty"
    assert "button1" in Widget1ComponentsContext.__annotations__
    assert Widget1ComponentsContext.__annotations__["button1"] == "ComponentProperty"


update_main_file_code = """import pandas as pd
from typing import List
from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from dropbase.database.connect import connect
from workspace.pages.page4.context import *
from workspace.pages.page4.state import *


class Table1(TableABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        db = connect("demo")
        query = "SELECT * FROM orders"
        table_data = db.query(query)
        table_df = pd.DataFrame(table_data)
        context.table1.data = table_df.to_dtable()
        return context

    def add(self, state: State, context: Context, row: Table1ColumnsState) -> Context:
        return context

    def update(
        self, state: State, context: Context, updates: List[Table1ColumnUpdate]
    ) -> Context:
        return context

    def delete(self, state: State, context: Context) -> Context:
        return context

    def on_row_change(self, state: State, context: Context) -> Context:
        return context


class Widget1(WidgetABC):

    def components_button1_on_click(self, state: State, context: Context) -> Context:
        return context

    def components_input1_on_submit(self, state: State, context: Context) -> Context:
        return context
"""


update_propreties_file_code = '{\n    "table1": {\n        "block_type": "table",\n        "label": "Table 1",\n        "name": "table1",\n        "description": "Query orders from demo db",\n        "columns": [],\n        "header": [],\n        "footer": [],\n        "w": 3,\n        "h": 1,\n        "x": 0,\n        "y": 0\n    },\n    "widget1": {\n        "block_type": "widget",\n        "label": "Widget 1",\n        "name": "widget1",\n        "description": null,\n        "type": "base",\n        "in_menu": true,\n        "components": [\n            {\n                "component_type": "button",\n                "label": "Button1",\n                "name": "button1",\n                "color": "blue",\n                "display_rules": null\n            },\n            {\n                "name": "input1",\n                "component_type": "input",\n                "type": "text",\n                "label": "Input1"\n            }\n        ],\n        "w": 1,\n        "h": 1,\n        "x": 3,\n        "y": 0\n    }\n}'
