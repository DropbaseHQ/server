import importlib
import json


def test_update_page(client):
    app_name, page_name = "pages", "page1"
    update_page_payload = {
        "app_name": app_name,
        "page_name": page_name,
        "properties": update_page_properties,
    }
    response = client.put("/page/", json=update_page_payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"Page {page_name} updated successfully"}

    # check if properties are updated in page properties.json
    page_properties = _get_page_properties(app_name, page_name)
    assert page_properties == update_page_properties

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


def test_save_columns(client):
    app_name, page_name, table_name = "pages", "page1", "table1"
    payload = {
        "app_name": app_name,
        "page_name": page_name,
        "table_name": table_name,
        "columns": save_columns,
    }
    response = client.post("/page/save_table_columns/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"Table {table_name} columns saved successfully"}

    # check if columns are saved in page properties.json
    page_properties = _get_page_properties(app_name, page_name)
    assert page_properties[table_name]["columns"] == save_columns

    # check if state has been updated
    state_module = importlib.import_module(f"workspace.{app_name}.{page_name}.state")
    importlib.reload(state_module)
    Table1ColumnsState = getattr(state_module, "Table1ColumnsState", None)
    assert Table1ColumnsState is not None
    for column in save_columns:
        assert column["name"] in Table1ColumnsState.__annotations__

    # check if context has been updated
    context_module = importlib.import_module(f"workspace.{app_name}.{page_name}.context")
    importlib.reload(context_module)
    Table1ColumnsContext = getattr(context_module, "Table1ColumnsContext", None)
    assert Table1ColumnsContext is not None
    for column in save_columns:
        assert column["name"] in Table1ColumnsContext.__annotations__
        assert Table1ColumnsContext.__annotations__[column["name"]] == "ColumnProperty"


def _get_page_properties(app_name, page_name):
    with open(f"workspace/{app_name}/{page_name}/properties.json", "r") as f:
        return json.load(f)


update_page_properties = {
    "table1": {
        "block_type": "table",
        "label": "Table 1",
        "name": "table1",
        "description": None,
        "columns": [],
        "header": [],
        "footer": [],
        "w": 3,
        "h": 1,
        "x": 0,
        "y": 0,
    },
    "widget1": {
        "block_type": "widget",
        "label": "Widget 1",
        "name": "widget1",
        "description": None,
        "components": [
            {
                "component_type": "button",
                "label": "Button1",
                "name": "button1",
                "color": "blue",
                "display_rules": None,
            },
            {"name": "input1", "component_type": "input", "type": "text", "label": "Input1"},
        ],
        "w": 1,
        "h": 1,
        "x": 3,
        "y": 0,
    },
}


save_columns = [
    {"name": "order_id", "data_type": "int64", "display_type": "integer", "column_type": "python"},
    {"name": "user_id", "data_type": "int64", "display_type": "integer", "column_type": "python"},
    {"name": "product_name", "data_type": "object", "display_type": "text", "column_type": "python"},
    {"name": "quantity", "data_type": "int64", "display_type": "integer", "column_type": "python"},
    {"name": "total_price", "data_type": "float64", "display_type": "float", "column_type": "python"},
    {"name": "order_date", "data_type": "object", "display_type": "text", "column_type": "python"},
]
