import pandas as pd

from context import Context
from page_script import PageBase


class Page(PageBase):
    def get_table1(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "created_at": ["2021-01-01", "2021-02-01", "2021-03-01"],
            }
        )

    def on_click_button1(self) -> Context:
        # TODO: implement this method
        return self.context

    def on_enter_input1(self) -> Context:
        # TODO: implement this method
        return self.context
