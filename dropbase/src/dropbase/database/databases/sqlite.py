import re

from sqlalchemy.engine import reflection
from sqlalchemy.sql import text

from dropbase.database.database import Database
from dropbase.models.table.sqlite_column import SqliteColumnProperty


class SqliteDatabase(Database):
    def __init__(self, creds: dict):
        super().__init__(creds)
        self.db_type = "sqlite"

    def _get_connection_url(self, creds: dict):
        return f"{creds.get('drivername')}:///{creds.get('host')}"

    def _get_db_schema(self):
        # # TODO: cache this, takes a while
        inspector = reflection.Inspector.from_engine(self.engine)
        databases = inspector.get_schema_names()

        # In Sqlite, this returns a list of databases, rather than schemas in Postgres

        db_schema = {}
        gpt_schema = {
            "metadata": {
                "default_schema": None,
            },
            "database": {},
        }

        for database in databases:
            ignore_schemas = [
                "information_schema",
                "sqlite",
                "performance_schema",
                "sys",
            ]
            if database in ignore_schemas:
                continue

            tables = inspector.get_table_names(schema=database)
            gpt_schema["database"][database] = {}
            db_schema[database] = {}

            for table_name in tables:
                columns = inspector.get_columns(table_name, schema=database)

                # get primary keys
                primary_keys = inspector.get_pk_constraint(table_name, schema=database)[
                    "constrained_columns"
                ]  # noqa

                # get foreign keys
                fk_constraints = inspector.get_foreign_keys(table_name, schema=database)
                foreign_keys = []
                for fk_constraint in fk_constraints:
                    foreign_keys.extend(fk_constraint["constrained_columns"])

                # get unique columns
                unique_constraints = inspector.get_unique_constraints(table_name, schema=database)
                unique_columns = []
                for unique_constraint in unique_constraints:
                    unique_columns.extend(unique_constraint["column_names"])

                db_schema[database][table_name] = {}
                for column in columns:
                    col_name = column["name"]
                    is_pk = col_name in primary_keys
                    db_schema[database][table_name][col_name] = {
                        "database_name": database,
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
                gpt_schema["database"][database][table_name] = [column["name"] for column in columns]

        return db_schema, gpt_schema

    def _get_column_names(self, user_sql: str) -> list[str]:
        if user_sql == "":
            return []
        user_sql = user_sql.strip("\n ;")

        user_sql = f"SELECT * FROM ({user_sql}) AS q LIMIT 1"
        with self.engine.connect().execution_options(autocommit=True) as conn:
            col_names = list(conn.execute(text(user_sql)).keys())
            cleaned_col_names = _remove_numerical_suffixes(col_names)
            # SQLITE automatically appends suffixes :1, :2 to manage duplicate column names,
            # which will interfere with detecting duplicates
        return cleaned_col_names

    def _get_table_path(self, col_data: SqliteColumnProperty) -> str:
        return f"{col_data.table_name}"


def _remove_numerical_suffixes(col_names):
    cleaned_col_names = [re.sub(r":\d+$", "", col_name) for col_name in col_names]
    return cleaned_col_names
