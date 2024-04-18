from abc import abstractmethod

import pandas as pd

from context import Context
from page_ABC import PageABC


class PageBase(PageABC):
    @abstractmethod
    def get_table1(self) -> pd.DataFrame:
        pass

    def update_table1(self) -> Context:
        pass

    def delete_table1(self) -> Context:
        pass

    @abstractmethod
    def on_click_button1(self) -> Context:
        pass

    @abstractmethod
    def on_enter_input1(self) -> Context:
        pass
