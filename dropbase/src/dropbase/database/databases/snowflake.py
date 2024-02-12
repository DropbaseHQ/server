from datetime import datetime, timezone

from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text

from dropbase.database.database import Database
from dropbase.models.table.pg_column import PgColumnDefinedProperty
from dropbase.schemas.edit_cell import CellEdit


class SnowflakeDatabase(Database):
    def __init__(self, creds: dict, schema: str = "public"):
        super().__init__(creds)
        self.schema = schema

    def _get_connection_url(self, creds: dict):
        query = {}
        for key in ["warehouse", "role", "dbschema"]:
            if key in creds:
                # If the key is 'dbschema', change it to 'schema' when adding to the query dictionary
                if key == "dbschema":
                    query["schema"] = creds.pop(key)
                else:
                    query[key] = creds.pop(key)

        return URL.create(query=query, **creds)

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
        sql = f"""UPDATE {self.schema}.{table}\n{set_claw}\n{where_claw} RETURNING *;"""  # Snowflake supports the returning clause
        values.update(keys)
        result = self.session.execute(text(sql), values)
        if auto_commit:
            self.commit()
        return [dict(x) for x in result.fetchall()]

    def select(self, table: str, where_clause: str = None, values: dict = None):
        if where_clause:
            sql = f"""SELECT * FROM {self.schema}.{table} WHERE {where_clause};"""  # The overall architecture of Snowflake is DB -> Schema -> Table (same as Postgres)
        else:
            sql = f"""SELECT * FROM {self.schema}.{table};"""

        if values is None:
            values = {}

        with self.engine.connect() as conn:
            result = conn.execute(text(sql), values)

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

    def query(self, sql: str):
        result = self.session.execute(text(sql))
        return [dict(row) for row in result.fetchall()]

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
