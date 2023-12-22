import json
import os
from typing import List

import pandas as pd
from jinja2 import Environment, meta
from sqlalchemy import text
from sqlalchemy.engine import Engine

from server.constants import DATA_PREVIEW_SIZE
from server.controllers.python_subprocess import format_process_result, run_process_task_unwrap
from server.controllers.utils import clean_df, connect_to_user_db, convert_df_to_resp_obj
from server.schemas.files import DataFile
from server.schemas.table import FilterSort, TableFilter, TablePagination, TableSort

cwd = os.getcwd()


def infer_column_type(column: pd.Series) -> str:
    parsed_column = json.loads(column.to_json(orient="records"))
    inferred_types = set()
    for item in parsed_column:
        if item is None:
            continue
        inferred_types.add(type(item))

    if len(inferred_types) == 1:
        return inferred_types.pop().__name__
    else:
        return str.__name__


def verify_state(app_name: str, page_name: str, state: dict):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "state": state,
    }
    return run_process_task_unwrap("verify_state", args)


def run_python_query(
    app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort
):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "file": file.dict(),
        "state": state,
        "filter_sort": filter_sort.dict(),
    }
    return run_process_task_unwrap("run_python_query", args)


def run_sql_query(app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort):
    verify_state(app_name, page_name, state)
    sql = get_table_sql(app_name, page_name, file.name)
    df = run_df_query(sql, file.source, state, filter_sort)
    # df = json.loads(df.to_json(orient="split"))
    res = convert_df_to_resp_obj(df)
    return format_process_result(res)


def run_sql_query_from_string(sql: str, source: str, app_name: str, page_name: str, state: dict):
    verify_state(app_name, page_name, state)
    df = run_df_query(sql, source, state)
    # df = json.loads(df.to_json(orient="split"))
    res = convert_df_to_resp_obj(df)
    return format_process_result(res)


def run_df_function(app_name: str, page_name: str, file: dict, state: dict):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "file": file,
        "state": state,
    }
    return run_process_task_unwrap("run_df_function", args)


def run_df_query(
    user_sql: str,
    source: str,
    state: dict,
    filter_sort: FilterSort = FilterSort(
        filters=[], sorts=[], pagination=TablePagination(page=0, page_size=DATA_PREVIEW_SIZE)
    ),
) -> pd.DataFrame:
    filter_sql, filter_values = prepare_sql(user_sql, state, filter_sort)
    res = query_db(filter_sql, filter_values, source)
    return process_query_result(res)


def process_query_result(res) -> pd.DataFrame:
    df = pd.DataFrame(res)
    df = clean_df(df)
    return df


def prepare_sql(user_sql: str, state: dict, filter_sort: FilterSort):
    sql = clean_sql(user_sql)
    sql = render_sql(sql, state)
    return apply_filters(sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination)


def clean_sql(sql):
    return sql.strip("\n ;")


def render_sql(user_sql: str, state: dict):
    env = Environment()
    template = env.from_string(user_sql)
    return template.render(**state["tables"])


def get_table_sql(app_name: str, page_name: str, file_name: str) -> str:
    path = cwd + f"/workspace/{app_name}/{page_name}/scripts/{file_name}.sql"
    with open(path, "r") as sql_file:
        sql = sql_file.read()
    return sql


def get_sql_variables(user_sql: str):
    env = Environment()
    parsed_content = env.parse(user_sql)
    return list(meta.find_undeclared_variables(parsed_content))


def query_db(sql, values, source_name):
    user_db_engine = connect_to_user_db(source_name)
    with user_db_engine.connect().execution_options(autocommit=True) as conn:
        res = conn.execute(text(sql), values).all()
    return res


def apply_filters(
    table_sql: str, filters: List[TableFilter], sorts: List[TableSort], pagination: TablePagination = {}
):
    # clean sql
    table_sql = table_sql.strip("\n ;")
    filter_sql = f"""WITH user_query as ({table_sql}) SELECT * FROM user_query\n"""

    # apply filters
    filter_values = {}
    if filters:
        filter_sql += "WHERE \n"

        filters_list = []
        for filter in filters:
            filter_value_name = f"{filter.column_name}_filter"
            match filter.condition:
                case "like":
                    filter.value = f"%{filter.value}%"
                case "is null" | "is not null":
                    # handle unary operators
                    filters_list.append(
                        f'user_query."{filter.column_name}" {filter.condition}'
                    )
                    continue

            filter_values[filter_value_name] = filter.value
            filters_list.append(
                f'user_query."{filter.column_name}" {filter.condition} :{filter_value_name}'
            )

        filter_sql += " AND ".join(filters_list)
    filter_sql += "\n"

    # apply sorts
    if sorts:
        filter_sql += "ORDER BY \n"
        sort_list = []
        for sort in sorts:
            sort_list.append(f'user_query."{sort.column_name}" {sort.value}')

        filter_sql += ", ".join(sort_list)
    filter_sql += "\n"

    if pagination:
        filter_sql += f"LIMIT {pagination.page_size + 1} OFFSET {pagination.page * pagination.page_size}"

    return filter_sql, filter_values


def get_column_names(user_db_engine: Engine, user_sql: str) -> list[str]:
    if user_sql == "":
        return []
    user_sql = user_sql.strip("\n ;")
    user_sql = f"SELECT * FROM ({user_sql}) AS q LIMIT 1"
    with user_db_engine.connect().execution_options(autocommit=True) as conn:
        col_names = list(conn.execute(text(user_sql)).keys())
    return col_names


def get_table_columns(app_name: str, page_name: str, file: dict, state: dict) -> List[dict]:
    if file.get("type") == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state)["result"]
        return get_df_columns(df)
    else:
        verify_state(app_name, page_name, state)
        sql = get_table_sql(app_name, page_name, file.get("name"))
        df = run_df_query(sql, file.get("source"), state, FilterSort(filters=[], sorts=[]))
        return get_df_columns(df)


def get_df_columns(df: pd.DataFrame) -> List[dict]:
    return [{"name": column, "type": infer_column_type(df[column])} for column in df.columns]
