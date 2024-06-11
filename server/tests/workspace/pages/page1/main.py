from typing import List

import pandas as pd

from dropbase.classes.tableABC import TableABC
from dropbase.classes.widgetABC import WidgetABC
from workspace.pages.page1.context import *
from workspace.pages.page1.state import *


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
