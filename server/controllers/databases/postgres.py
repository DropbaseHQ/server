from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text

from server.controllers.database import Database
from server.models.table.pg_column import PgColumnDefinedProperty
from server.schemas.edit_cell import CellEdit


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

    def _validate_smart_cols(self, smart_cols: dict[str, dict], user_sql: str) -> list[str]:  # noqa
        # Will delete any columns that are invalid from smart_cols
        primary_keys = self._get_primary_keys(smart_cols)
        validated = []
        for col_name, col_data in smart_cols.items():
            col_data = PgColumnDefinedProperty(**col_data)
            pk_name = primary_keys.get(self._get_table_path(col_data))
            if pk_name:
                validation_sql = _get_fast_sql(
                    user_sql,
                    col_name,
                    col_data.schema_name,
                    col_data.table_name,
                    col_data.column_name,
                    pk_name,
                )
            else:
                validation_sql = _get_slow_sql(
                    user_sql,
                    col_name,
                    col_data.schema_name,
                    col_data.table_name,
                    col_data.column_name,
                )
            try:
                with self.engine.connect().execution_options(autocommit=True) as conn:
                    # On SQL programming error, we know that the smart cols are invalid,
                    # no need to catch them
                    res = conn.execute(text(validation_sql)).all()
                    if res:
                        validated.append(col_name)
                if not res[0][0]:
                    raise "Invalid column"
            except (SQLAlchemyError):
                continue
        return validated

    def _get_primary_keys(self, smart_cols: dict[str, dict]) -> dict[str, dict]:
        primary_keys = {}
        for col_data in smart_cols.values():
            col_data = PgColumnDefinedProperty(**col_data)
            if col_data.primary_key:
                primary_keys[self._get_table_path(col_data)] = col_data.column_name
        return primary_keys

    def _get_table_path(self, col_data: PgColumnDefinedProperty) -> str:
        return f"{col_data.schema_name}.{col_data.table_name}"

    def _update_value(self, edit: CellEdit):
        try:
            columns_name = edit.column_name
            # NOTE: client sends columns as a list of column objects. we need to convert it to a dict
            columns_dict = {col.column_name: col for col in edit.columns}
            column = columns_dict[columns_name]

            values = {
                "new_value": edit.new_value,
                "old_value": edit.old_value,
            }
            prim_key_list = []
            edit_keys = column.edit_keys
            for key in edit_keys:
                pk_col = columns_dict[key]
                prim_key_list.append(f"{pk_col.column_name} = :{pk_col.column_name}")
                values[pk_col.column_name] = edit.row[pk_col.name]
            prim_key_str = " AND ".join(prim_key_list)

            sql = f"""UPDATE "{column.schema_name}"."{column.table_name}"
            SET {column.column_name} = :new_value
            WHERE {prim_key_str}"""

            # TODO: add check for prev column value
            # AND {column.column_name} = :old_value

            with self.engine.connect() as conn:
                result = conn.execute(text(sql), values)
                conn.commit()
                if result.rowcount == 0:
                    raise Exception("No rows were updated")
            return f"Updated {edit.column_name} from {edit.old_value} to {edit.new_value}", True
        except Exception as e:
            return (
                f"Failed to update {edit.column_name} from {edit.old_value} to {edit.new_value}. Error: {str(e)}",  # noqa
                False,
            )

    def _run_query(self, sql: str, values: dict):
        with self.engine.connect().execution_options(autocommit=True) as conn:
            res = conn.execute(text(sql), values).all()
        return res


# helper functions


def _get_fast_sql(
    user_sql: str,
    name: str,
    schema_name: str,
    table_name: str,
    column_name: str,
    table_pk_name: str,
) -> str:
    # Query that results in [(1,)] if valid, [(0,)] if false
    # NOTE: validate name of the column in user query (name) against column name in table (column_name)
    return f"""
    WITH uq as ({user_sql})
    SELECT min(
        CASE WHEN
            t.{column_name} = uq.{name} or
            t.{column_name} is null and uq.{name} is null
        THEN 1 ELSE 0 END
    ) as equal
    FROM {schema_name}.{table_name} t
    INNER join uq on t.{table_pk_name} = uq.{table_pk_name}
    LIMIT 500;
    """


def _get_slow_sql(
    user_sql: str,
    name: str,
    schema_name: str,
    table_name: str,
    column_name: str,
) -> str:
    # Query that results in [(True,)] if valid, [(False,)] if false
    # NOTE: validate name of the column in user query (name) against column name in table (column_name)
    # NOTE: limit user query to 500 rows to improve performance
    return f"""
    WITH uq as ({user_sql})
    SELECT CASE WHEN count(t.{column_name}) = 0 THEN true ELSE false END
    FROM {schema_name}.{table_name} t
    WHERE t.{column_name} not in (select uq.{name} from uq LIMIT 500);
    """
