from abc import ABC, abstractmethod

from sqlalchemy.orm import scoped_session, sessionmaker

from server.controllers.utils import connect_to_user_db
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.table import ConvertTableRequest
from server.schemas.query import RunSQLRequest

class Database(ABC):
   def __init__(self, database: str, schema: str = "public"):
       self.source = database
       self.schema = schema
       self.engine = connect_to_user_db(database)
       self.session_obj = scoped_session(sessionmaker(bind=self.engine))


   def __enter__(self):
       self.session = self.session_obj()
       return self


   def __exit__(self, type, value, traceback):
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
   def filter_and_sort(self, table: str, filter_clauses: list, sort_by: str = None, ascending: bool = True):
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