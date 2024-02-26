from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from dropbase.schemas.edit_cell import CellEdit
from dropbase.schemas.table import TableFilter, TablePagination, TableSort


class Database(ABC):
    def __init__(self, creds: dict):
        # get creds
        connection_url = self._get_connection_url(creds)
        # create engine and session
        self.engine = create_engine(connection_url, future=True)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def __exit__(self):
        self.session.close()
        self.engine.dispose()

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def rollback(self):
        self.session.rollback()

    @abstractmethod
    def _get_connection_url(self, creds):
        pass

    @abstractmethod
    def update(self, table: str, keys: dict, values: dict, auto_commit: bool = False):
        pass

    @abstractmethod
    def select(self, table: str, where_clause: str = None, values: dict = None):
        pass

    @abstractmethod
    def insert(self, table: str, values: dict, auto_commit: bool = False):
        pass

    @abstractmethod
    def delete(self, table: str, keys: dict, auto_commit: bool = False):
        pass

    @abstractmethod
    def query(self, sql: str):
        pass

    @abstractmethod
    def execute(self, sql: str, values: dict = None):
        pass

    @abstractmethod
    def filter_and_sort(
        self, table: str, filter_clauses: list, sort_by: str = None, ascending: bool = True
    ):
        pass

    @abstractmethod
    def _get_db_schema(self):
        pass

    @abstractmethod
    def _get_column_names(self, user_sql: str):
        pass

    @abstractmethod
    def _validate_smart_cols(self, smart_cols: dict[str, dict], user_sql: str):
        pass

    @abstractmethod
    def _update_value(self, edit: CellEdit):
        pass

    @abstractmethod
    def _run_query(self, sql: str, values: dict):
        pass

    @abstractmethod
    def _apply_filters(
        self,
        table_sql: str,
        filters: List[TableFilter],
        sorts: List[TableSort],
        pagination: TablePagination = {},
    ):
        pass

    def _detect_col_display_type(self, col_type: str):
        if "float" in col_type:
            return "float"
        elif col_type in ["real", "double", "double precision", "decimal", "numeric"]:
            return "float"
        elif "int" in col_type:
            return "integer"
        elif col_type == "date":
            return "date"
        elif col_type == "time":
            return "time"
        elif col_type == "datetime":
            return "datetime"
        elif "timestamp" in col_type:
            return "datetime"
        elif "bool" in col_type:
            return "boolean"
        else:
            return "text"
