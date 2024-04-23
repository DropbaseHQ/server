import pandas as pd

from dropbase.helpers.tableABC import TableABC
from dropbase.helpers.widgetABC import WidgetABC

from ..context import Context


class Table1(TableABC):
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


class Widget1(WidgetABC):
    pass


class Table2(TableABC):
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame()


class Table3(TableABC):
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame()


class Table4(TableABC):
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame()


class Table5(TableABC):
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame()
