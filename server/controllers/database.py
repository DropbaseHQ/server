import functools
from abc import ABC, abstractmethod

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from server.constants import WORKSPACE_SOURCES
from server.controllers.sources import db_type_to_class, db_type_to_connection
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.query import RunSQLRequest
from server.schemas.table import ConvertTableRequest


@functools.lru_cache
def connect_to_user_db(source_name: str):
    creds = WORKSPACE_SOURCES.get(source_name)
    creds_type = creds.get("type")

    CredsClass = db_type_to_class.get(creds_type)
    creds = CredsClass(**creds)

    if CredsClass is None:
        raise ValueError(f"Unsupported database type: {creds_type}")

    db_class = db_type_to_connection.get(creds_type)
    db_instance = db_class(creds)

    return db_instance.get_engine()


class Database(ABC):
    def __init__(self, database: str, schema: str = "public"):
        self.source = database
        self.schema = schema
        creds = WORKSPACE_SOURCES.get(database)
        self.creds = self._define_creds(creds)
        self.engine = create_engine(self._get_connection_url(), future=True)
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
    def _define_creds(self, creds: dict):
        pass

    @abstractmethod
    def _get_connection_url(self):
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
