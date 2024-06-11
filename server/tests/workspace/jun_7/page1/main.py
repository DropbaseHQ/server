import os
from typing import List

import pandas as pd

from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from dropbase.database.connect import connect
from workspace.jun_8.page1.context import *
from workspace.jun_8.page1.state import *


class Table1(TableABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self, state: State, context: Context):
        db = connect("demo")
        table_data = db.query("SELECT * FROM orders")
        table_df = pd.DataFrame(table_data)
        context.table1.data = table_df.to_dtable()
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
    def components_input1_on_submit(self, state: State, context: Context) -> Context:
        return context

    def components_button1_on_click(self, state: State, context: Context) -> Context:
        db = connect("demo")
        input_value = state.widget1.components.input1
        table_data = db.query(
            "SELECT * FROM orders WHERE product_name = :product_name", {"product_name": input_value}
        )
        table_df = pd.DataFrame(table_data)
        context.table1.data = table_df.to_dtable()
        return context
