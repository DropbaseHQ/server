from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect
from sqlalchemy.sql import text

from server.controllers.database import Database
from server.models.table.pg_column import PgColumnDefinedProperty
from server.schemas.edit_cell import CellEdit


class MySqlDatabase(Database):
    def _get_connection_url(self, creds: dict):
        return URL.create(**creds)

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
        sql = f"""UPDATE {self.schema}.{table}\n{set_claw}\n{where_claw};"""  # MySQL does not support RETURN keyword
        values.update(keys)
        result = self.session.execute(text(sql), values)
        if auto_commit:
            self.commit()
        return result.rowcount  # MySQL doesn't support RETURNING *, so we can't directly return row data

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
       VALUES (:{', :'.join(keys)});"""
        row = self.session.execute(text(sql), values)
        last_inserted_id = row.lastrowid
        if auto_commit:
            self.commit()
        return {"id": last_inserted_id}

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

    # MySQL Compatible up to here

    def _get_db_schema(self):
        pass

    def _get_column_names(self, user_sql: str) -> list[str]:
        pass

    def _validate_smart_cols(self, smart_cols: dict[str, dict], user_sql: str) -> list[str]:  # noqa
        pass

    def _get_primary_keys(self, smart_cols: dict[str, dict]) -> dict[str, dict]:
        pass

    def _get_table_path(self, col_data: PgColumnDefinedProperty) -> str:
        pass

    def _update_value(self, edit: CellEdit):
        pass

    def _run_query(self, sql: str, values: dict):
        with self.engine.connect().execution_options(autocommit=True) as conn:
            res = conn.execute(text(sql), values).all()
        return res


# helper functions --> if these helper functions are compatible with mysql maybe move it to utils?


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
