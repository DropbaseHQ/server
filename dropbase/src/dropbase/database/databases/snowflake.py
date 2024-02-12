from datetime import datetime, timezone

from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text

from dropbase.database.database import Database
from dropbase.models.table.snowflake_column import SnowflakeColumnDefinedProperty
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

    def _get_db_schema(self):
        # TODO: cache this, takes a while
        inspector = inspect(self.engine)
        schemas = inspector.get_schema_names()
        default_search_path = inspector.default_schema_name

        db_schema = {}
        gpt_schema = {
            "metadata": {
                "default_schema": default_search_path,
            },
            "schema": {},
        }

        for schema in schemas:
            if schema == "information_schema":
                continue
            tables = inspector.get_table_names(schema=schema)
            gpt_schema["schema"][schema] = {}
            db_schema[schema] = {}

            for table_name in tables:
                columns = inspector.get_columns(table_name, schema=schema)

                # get primary keys
                primary_keys = inspector.get_pk_constraint(table_name, schema=schema)[
                    "constrained_columns"
                ]  # noqa

                # get foreign keys
                fk_constraints = inspector.get_foreign_keys(table_name, schema=schema)
                foreign_keys = []
                for fk_constraint in fk_constraints:
                    foreign_keys.extend(fk_constraint["constrained_columns"])

                # get unique columns
                unique_constraints = inspector.get_unique_constraints(table_name, schema=schema)
                unique_columns = []
                for unique_constraint in unique_constraints:
                    unique_columns.extend(unique_constraint["column_names"])

                db_schema[schema][table_name] = {}
                for column in columns:
                    col_name = column["name"]
                    is_pk = col_name in primary_keys
                    db_schema[schema][table_name][col_name] = {
                        "schema_name": schema,
                        "table_name": table_name,
                        "column_name": col_name,
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                        "unique": col_name in unique_columns,
                        "primary_key": is_pk,
                        "foreign_key": col_name in foreign_keys,
                        "default": column["default"],
                        "edit_keys": primary_keys if not is_pk else [],
                    }
                gpt_schema["schema"][schema][table_name] = [column["name"] for column in columns]
        return db_schema, gpt_schema
