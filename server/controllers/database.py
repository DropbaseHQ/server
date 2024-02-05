from abc import ABC, abstractmethod

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from server.constants import WORKSPACE_SOURCES
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.query import RunSQLRequest
from server.schemas.table import ConvertTableRequest


class Database(ABC):
    def __init__(self, database: str, schema: str = "public"):
        # set source and schema
        self.source = database
        self.schema = schema
        # get creds
        creds = WORKSPACE_SOURCES.get(database)
        connection_url = self._get_connection_url(creds.dict())
        # create engine and session
        self.engine = create_engine(connection_url, future=True)
        self.session_obj = scoped_session(sessionmaker(bind=self.engine))

    def __enter__(self):
        self.session = self.session_obj()
        return self

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
    def filter_and_sort(
        self, table: str, filter_clauses: list, sort_by: str = None, ascending: bool = True
    ):
        pass

    @abstractmethod
    def execute_custom_query(self, sql: str, values: dict = None):
        pass

    @abstractmethod
    def convert_sql_table(req: ConvertTableRequest, router: DropbaseRouter):
        pass

    @abstractmethod
    def run_sql_query_from_string(req: RunSQLRequest):
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
