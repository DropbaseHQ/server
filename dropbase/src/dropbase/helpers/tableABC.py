from abc import ABC, abstractmethod

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
        self.state = kwargs.get("state")
        self.context = kwargs.get("context")

    @abstractmethod
    def get_data(self):
        pass

    def udpate_row(self, edits: list[CellEdit]):
        pass

    def create_row(self, row: dict):
        pass

    def delete_row(self, row: dict):
        pass

    def handle_updates(self, updates: list):
        for update in updates:
            self.update_row(update)
        return self.context

    # generic methods used by dropbase
    def get_table_data(self):
        self.context.__getattribute__(self.name).data = self.get_data().to_dtable()
        return self.context

    def load_page(self):
        # todo: get tables from context
        tables = self.get_table_names()
        for table in tables:
            self.get_table_data(table)
        return self.context
