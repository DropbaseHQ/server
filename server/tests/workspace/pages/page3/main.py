from typing import List

import pandas as pd

from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from dropbase.database.connect import connect
from workspace.pages.page3.context import *
from workspace.pages.page3.state import *


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
        db = connect("demo")
        for update in updates:
            new_data = update.new.dict()
            set_clauses = ", ".join([f"{k} = :{k}" for k in new_data.keys() if k != "order_id"])
            sql_query = f"""
                UPDATE orders
                SET {set_clauses}
                WHERE order_id = :order_id
            """
            try:
                db.execute(sql_query, new_data)
            except Exception as e:
                context.page.message = f"Error updating record: {str(e)}"
                context.page.message_type = "error"
                return context
        context.page.message = "Records updated successfully."
        context.page.message_type = "success"
        return context

    def delete(self, state: State, context: Context) -> Context:
        return context

    def on_row_change(self, state: State, context: Context) -> Context:
        return context

    def header_button1_on_click(self, state: State, context: Context) -> Context:
        context.page.message = "Header Button 1 clicked."
        return context


class Widget1(WidgetABC):
    def components_input1_on_submit(self, state: State, context: Context) -> Context:
        context.page.message = f"Input1 submitted: {state.widget1.components.input1}"
        return context

    def components_button1_on_click(self, state: State, context: Context) -> Context:
        context.page.message = "Button1 clicked."
        return context
