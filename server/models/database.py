from abc import ABC, abstractmethod

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

from server.requests.dropbase_router import DropbaseRouter
from server.schemas.table import ConvertTableRequest
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest

from server.controllers.page import get_page_state_context
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.validation import validate_smart_cols
from server.controllers.utils import connect_to_user_db, get_column_names, get_table_data_fetcher
from server.controllers.source import get_db_schema
from server.controllers.run_sql import get_sql_from_file, render_sql, verify_state, run_df_query
from server.controllers.dataframe import convert_df_to_resp_obj
from server.controllers.python_subprocess import format_process_result

from server.constants import pg_base_type_mapper

class BaseDatabase(ABC):
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

class PostgresDatabase(BaseDatabase):
   # Removed commit, rollback, etc as abstract method, add back if necessary
   def update(self, table: str, keys: dict, values: dict, auto_commit: bool = False):
       value_keys = list(values.keys())
       if len(value_keys) > 1:
           set_claw = f"SET ({', '.join(value_keys)}) = (:{', :'.join(value_keys)})"
       else:
           set_claw = f"SET {value_keys[0]} = :{value_keys[0]}"
       key_keys = list(keys.keys())
       if len(key_keys) > 1:
           where_claw = f"WHERE ({', '.join(key_keys)}) = (:{', :'.join(key_keys)})"
       else:
           where_claw = f"WHERE {key_keys[0]} = :{key_keys[0]}"
       sql = f"""UPDATE {self.schema}.{table}\n{set_claw}\n{where_claw} RETURNING *;"""
       values.update(keys)
       result = self.session.execute(text(sql), values)
       if auto_commit:
           self.commit()
       return [dict(x) for x in result.fetchall()]
  
   def select(self, table: str, where_clause: str = None, values: dict = None):
       if where_clause:
           sql = f"""SELECT * FROM {self.schema}.{table} WHERE {where_clause};"""
       else:
           sql = f"""SELECT * FROM {self.schema}.{table};"""


       if values is None:
           values = {}


       result = self.session.execute(text(sql), values)
       return [dict(row) for row in result.fetchall()]


   def insert(self, table: str, values: dict, auto_commit: bool = False):
       keys = list(values.keys())
       sql = f"""INSERT INTO {self.schema}.{table} ({', '.join(keys)})
       VALUES (:{', :'.join(keys)})
       RETURNING *;"""
       row = self.session.execute(text(sql), values)
       if auto_commit:
           self.commit()
       return dict(row.fetchone())


   def delete(self, table: str, keys: dict, auto_commit: bool = False):
       key_keys = list(keys.keys())
       if len(key_keys) > 1:
           where_claw = f"WHERE ({', '.join(key_keys)}) = (:{', :'.join(key_keys)})"
       else:
           where_claw = f"WHERE {key_keys[0]} = :{key_keys[0]}"
       sql = f"""DELETE FROM {self.schema}.{table}\n{where_claw};"""
       res = self.session.execute(text(sql), keys)
       if auto_commit:
           self.commit()
       return res.rowcount


   def filter_and_sort(self, table: str, filter_clauses: list, sort_by: str = None, ascending: bool = True):
       sql = f"""SELECT * FROM {self.schema}.{table}"""
       if filter_clauses:
           sql += " WHERE " + " AND ".join(filter_clauses)
       if sort_by:
           sql += f" ORDER BY {sort_by} {'ASC' if ascending else 'DESC'}"
       result = self.session.execute(text(sql))
       return [dict(row) for row in result.fetchall()]


   def execute_custom_query(self, sql: str, values: dict = None):
       result = self.session.execute(text(sql), values if values else {})
       return [dict(row) for row in result.fetchall()]


   def convert_sql_table(req: ConvertTableRequest, router: DropbaseRouter):
       try:
           # get db schema
           properties = read_page_properties(req.app_name, req.page_name)
           file = get_table_data_fetcher(properties["files"], req.table.fetcher)
           file = DataFile(**file)


           user_db_engine = connect_to_user_db(file.source)
           db_schema, gpt_schema = get_db_schema(user_db_engine)


           # get columns
           user_sql = get_sql_from_file(req.app_name, req.page_name, file.name)
           user_sql = render_sql(user_sql, req.state)
           column_names = get_column_names(user_db_engine, user_sql)


           # get columns from file
           get_smart_table_payload = {
               "user_sql": user_sql,
               "column_names": column_names,
               "gpt_schema": gpt_schema,
               "db_schema": db_schema,
           }


           resp = router.misc.get_smart_columns(get_smart_table_payload)
           if resp.status_code != 200:
               return resp.text
           smart_cols = resp.json().get("columns")

           for column in smart_cols.values():
               column["column_type"] = column.pop("type")

           # validate columns
           validated = validate_smart_cols(user_db_engine, smart_cols, user_sql)
           column_props = [value for name, value in smart_cols.items() if name in validated]

           for column in column_props:
               column["display_type"] = pg_base_type_mapper.get(column["column_type"])

           for table in properties["tables"]:
               if table["name"] == req.table.name:
                   table["smart"] = True
                   table["columns"] = column_props

           # update properties
           update_properties(req.app_name, req.page_name, properties)

           # get new steate and context
           return get_page_state_context(req.app_name, req.page_name), 200

       except Exception as e:
           return str(e), 500


   def run_sql_query_from_string(req: RunSQLRequest):
       verify_state(req.app_name, req.page_name, req.state)
       df = run_df_query(req.file_content, req.source, req.state)
       res = convert_df_to_resp_obj(df)
       return format_process_result(res)