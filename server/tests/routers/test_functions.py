import time

# NOTE: this test requires a running redis server

page_name, app_name = "page1", "functions"


def test_run_function(client):
    payload = {
        "page_name": page_name,
        "app_name": app_name,
        "state": state_obj,
        "action": "get",
        "resource": "table1",
    }
    response = client.post("/function/class/", json=payload)
    assert response.status_code == 202

    job_id = response.json()["job_id"]
    time.sleep(1)

    response = client.get(f"/status/{job_id}")
    assert response.status_code == 200
    context = response.json().get("context")
    assert context == resopnse_context


def test_run_function_string(client):
    payload = {
        "state": state_obj,
        "code": run_code_string_code_correct,
        "test": run_code_string_code_test,
    }
    response = client.post("/function/string/", json=payload)
    assert response.status_code == 202

    job_id = response.json()["job_id"]
    time.sleep(1)

    response = client.get(f"/status/{job_id}")
    assert response.status_code == 200
    context = response.json().get("context")
    assert context == resopnse_context


def test_run_function_string_error(client):
    payload = {
        "state": state_obj,
        "code": run_code_string_code_error,
        "test": run_code_string_code_test,
    }
    response = client.post("/function/string/", json=payload)
    assert response.status_code == 202

    job_id = response.json()["job_id"]
    time.sleep(1)

    response = client.get(f"/status/{job_id}")
    assert response.status_code == 500
    response = response.json()
    assert response["message"] == "division by zero"
    assert response["traceback"] is not None


def test_run_function_string_print(client):
    payload = {
        "state": state_obj,
        "code": run_code_string_code_print,
        "test": run_code_string_code_test,
    }
    response = client.post("/function/string/", json=payload)
    assert response.status_code == 202

    job_id = response.json()["job_id"]
    time.sleep(1)

    response = client.get(f"/status/{job_id}")
    assert response.status_code == 200
    response = response.json()
    assert response["message"] == "Job completed"
    assert response["stdout"] == "hello\n"
    assert isinstance(response["context"], dict)


state_obj = {
    "table1": {
        "columns": {
            "order_id": None,
            "user_id": None,
            "product_name": None,
            "quantity": None,
            "total_price": None,
            "order_date": None,
        },
        "header": {},
        "footer": {},
    },
    "widget1": {"components": {}},
}

resopnse_context = {
    "page": {"message": None, "message_type": None},
    "table1": {
        "data": {
            "columns": [
                {
                    "name": "order_id",
                    "data_type": "int64",
                    "display_type": "integer",
                    "column_type": "python",
                },
                {
                    "name": "user_id",
                    "data_type": "int64",
                    "display_type": "integer",
                    "column_type": "python",
                },
                {
                    "name": "product_name",
                    "data_type": "object",
                    "display_type": "text",
                    "column_type": "python",
                },
                {
                    "name": "quantity",
                    "data_type": "int64",
                    "display_type": "integer",
                    "column_type": "python",
                },
                {
                    "name": "total_price",
                    "data_type": "int64",
                    "display_type": "integer",
                    "column_type": "python",
                },
                {
                    "name": "order_date",
                    "data_type": "object",
                    "display_type": "text",
                    "column_type": "python",
                },
            ],
            "index": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "data": [
                [1, 1, "Laptop", 123, 1500, "2023-01-15"],
                [3, 2, "Keyboard", 1, 50, "2023-03-12"],
                [4, 3, "Headphones", 2, 75, "2023-04-20"],
                [5, 3, "Monitor", 1, 300, "2023-05-01"],
                [6, 4, "Tablet", 1, 200, "2023-06-08"],
                [7, 5, "Printer", 1, 120, "2023-07-15"],
                [8, 6, "External HDD", 1, 80, "2023-08-22"],
                [9, 7, "Camera", 1, 350, "2023-09-30"],
                [10, 8, "Smartphone", 1, 600, "2023-10-10"],
            ],
            "type": "python",
        },
        "message": None,
        "message_type": None,
        "reload": False,
        "columns": {
            "order_id": {"visible": None},
            "user_id": {"visible": None},
            "product_name": {"visible": None},
            "quantity": {"visible": None},
            "total_price": {"visible": None},
            "order_date": {"visible": None},
        },
        "header": {},
        "footer": {},
    },
    "widget1": {"visible": None, "message": None, "message_type": None, "components": {}},
}

run_code_string_code_correct = """import pandas as pd
from typing import List
from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from workspace.functions.page1.context import *
from workspace.functions.page1.state import *
from dropbase.database.connect import connect


class Table1(TableABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        db = connect("test")
        table_data = db.query("select * from orders")
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
    pass
"""

run_code_string_code_error = """import pandas as pd
from typing import List
from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from workspace.functions.page1.context import *
from workspace.functions.page1.state import *
from dropbase.database.connect import connect


class Table1(TableABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        1/0
        db = connect("test")
        table_data = db.query("select * from orders")
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
    pass
"""

run_code_string_code_print = """import pandas as pd
from typing import List
from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from workspace.functions.page1.context import *
from workspace.functions.page1.state import *
from dropbase.database.connect import connect


class Table1(TableABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        print('hello')
        db = connect("test")
        table_data = db.query("select * from orders")
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
    pass
"""

run_code_string_code_test = """table1 = Table1()
table1.get(state, context)"""
