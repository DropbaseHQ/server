from abc import ABC, abstractmethod

import pandas as pd

from context import Context
from state import State


class PageABC(ABC):
    def __init__(self, state: State):
        self.state = State(**state)

    @abstractmethod
    def get_table1(self) -> pd.DataFrame:
        pass

    def update_table1(self) -> Context:
        pass

    def delete_table1(self) -> Context:
        pass

    @abstractmethod
    def get_widget1(self) -> pd.DataFrame:
        pass

    def update_widget1(self) -> Context:
        pass

    def delete_widget1(self) -> Context:
        pass
