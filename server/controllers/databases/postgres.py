import json
import traceback

from sqlalchemy.engine import URL
from sqlalchemy.sql import text

from server.controllers.database import Database
from server.controllers.dataframe import convert_df_to_resp_obj
from server.controllers.page import get_page_state_context
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.redis import r
from server.controllers.run_sql import get_sql_from_file, render_sql, run_df_query, verify_state
from server.controllers.source import get_db_schema
from server.controllers.utils import get_column_names, get_table_data_fetcher
from server.controllers.validation import validate_smart_cols
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest
from server.schemas.table import ConvertTableRequest


class PostgresDatabase(Database):
    def _get_connection_url(self, creds: dict):
        return URL.create(**creds)

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

    def filter_and_sort(
        self, table: str, filter_clauses: list, sort_by: str = None, ascending: bool = True
    ):
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

    def convert_sql_table(self, req: ConvertTableRequest, router: DropbaseRouter):
        try:
            # get db schema
            properties = read_page_properties(req.app_name, req.page_name)
            file = get_table_data_fetcher(properties["files"], req.table.fetcher)
            file = DataFile(**file)

            db_schema, gpt_schema = get_db_schema(self.engine)

            # get columns
            user_sql = get_sql_from_file(req.app_name, req.page_name, file.name)
            user_sql = render_sql(user_sql, req.state)
            column_names = get_column_names(self.engine, user_sql)

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
            # NOTE: columns type in smart_cols dict (from chatgpt) is called type.
            # do not confuse it with column_type, which we use internally

            # rename type to column_type
            for column in smart_cols.values():
                column["column_type"] = column.pop("type")

            # validate columns
            validated = validate_smart_cols(self.engine, smart_cols, user_sql)
            column_props = [value for name, value in smart_cols.items() if name in validated]

            for column in column_props:
                column["display_type"] = self._detect_col_display_type(column["column_type"])

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

    def run_sql_query_from_string(self, req: RunSQLRequest, job_id: str):
        response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}
        try:
            verify_state(req.app_name, req.page_name, req.state)
            df = run_df_query(self.engine, req.file_content, req.state)
            res = convert_df_to_resp_obj(df)
            r.set(job_id, json.dumps(res))

            response["data"] = res["data"]
            response["columns"] = res["columns"]
            response["message"] = "job completed"
            response["type"] = "table"

            response["status_code"] = 200
            return {"message": "success"}
        except Exception as e:
            response["traceback"] = traceback.format_exc()
            response["message"] = str(e)
            response["type"] = "error"

            response["status_code"] = 200
        finally:
            # pass
            r.set(job_id, json.dumps(response))
