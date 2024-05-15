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
    def get(self, state, context):
        return context

    def update(self, state, context, edits: List[CellEdit]):
        return context

    def add(self, state, context, row: dict):
        return context

    def delete(self, state, context, row: dict):
        return context

    def on_row_change(self, state, context):
        return context
