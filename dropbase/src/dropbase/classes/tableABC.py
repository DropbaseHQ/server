from abc import ABC, abstractmethod

import pandas as pd

from dropbase.helpers.dataframe import to_dtable

pd.DataFrame.to_dtable = to_dtable


class TableABC(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get(self, state, context):
        return context

    def update(self, state, context, updates):
        return context

    def add(self, state, context, row):
        return context

    def delete(self, state, context):
        return context

    def on_row_change(self, state, context):
        return context
