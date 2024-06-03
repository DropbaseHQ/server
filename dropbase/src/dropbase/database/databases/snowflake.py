from sqlalchemy.engine import URL
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text

from dropbase.database.database import Database


class SnowflakeDatabase(Database):
    def __init__(self, creds: dict, schema: str = "public"):
        super().__init__(creds)
        self.schema = schema
        self.db_type = "snowflake"

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

    def _get_column_names(self, user_sql: str) -> list[str]:
        if user_sql == "":
            return []
        user_sql = user_sql.strip("\n ;")
        user_sql = f"SELECT * FROM ({user_sql}) AS q LIMIT 1"
        with self.engine.connect().execution_options(autocommit=True) as conn:
            col_names = list(conn.execute(text(user_sql)).keys())
        return col_names
