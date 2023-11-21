from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class PgColumn(BaseModel):
    name: str
    type: str = None
    schema_name: str = None
    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    edit_keys: list = []


class ColumnPathInferenceError(BaseException):
    pass


def get_fast_sql(
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


def get_slow_sql(
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


def get_table_path(col_data: PgColumn) -> str:
    return f"{col_data.schema_name}.{col_data.table_name}"


def get_primary_keys(smart_cols: dict[str, dict]) -> dict[str, dict]:
    primary_keys = {}
    for col_data in smart_cols.values():
        col_data = PgColumn(**col_data)
        if col_data.primary_key:
            primary_keys[get_table_path(col_data)] = col_data.column_name
    return primary_keys


def validate_smart_cols(user_db_engine, smart_cols: dict[str, dict], user_sql: str) -> list[str]:
    # Will delete any columns that are invalid from smart_cols
    primary_keys = get_primary_keys(smart_cols)
    validated = []
    for col_name, col_data in smart_cols.items():
        col_data = PgColumn(**col_data)
        pk_name = primary_keys.get(get_table_path(col_data))
        if pk_name:
            validation_sql = get_fast_sql(
                user_sql,
                col_name,
                col_data.schema_name,
                col_data.table_name,
                col_data.column_name,
                pk_name,
            )
        else:
            validation_sql = get_slow_sql(
                user_sql,
                col_name,
                col_data.schema_name,
                col_data.table_name,
                col_data.column_name,
            )
        try:
            with user_db_engine.connect().execution_options(autocommit=True) as conn:
                # On SQL programming error, we know that the smart cols are invalid,
                # no need to catch them
                res = conn.execute(text(validation_sql)).all()
                if res:
                    validated.append(col_name)
            if not res[0][0]:
                # invalid
                raise ColumnPathInferenceError
        except (SQLAlchemyError, ColumnPathInferenceError):
            continue
    return validated
