from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from dropbase.helpers.dataframe import to_dtable
from dropbase.schemas.edit_cell import CellEdit

pd.DataFrame.to_dtable = to_dtable


class TableABC(ABC):
    def __init__(self, **kwargs):
        # todo: maybe change to pydantic model
        self.name = kwargs.get("name")
        self.app_name = kwargs.get("app_name")
        self.page_name = kwargs.get("page_name")

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get(self, state, context):
        pass

    def update(self, state, context, edits: List[CellEdit]):
        pass

    def add(self, state, context, row: dict):
        pass

    def delete(self, state, context, row: dict):
        pass

    def on_row_change(self, state, context):
        pass

    def load_page(self, state, context):
        # todo: get tables from context
        tables = self.get_table_names()
        for table in tables:
            self.get_table_data(table)
        return self.context
