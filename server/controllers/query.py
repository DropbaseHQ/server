import re
from typing import List

import pandas as pd
from jinja2 import Environment
from sqlalchemy import text
from sqlalchemy.engine import Engine

from server.constants import DATA_PREVIEW_SIZE, cwd
from server.controllers.dataframe import convert_df_to_resp_obj
from server.controllers.properties import read_page_properties
from server.controllers.python_subprocess import (
    format_process_result,
    run_process_task_unwrap,
)
from server.controllers.utils import (
    clean_df,
    connect_to_user_db,
    get_table_data_fetcher,
)
from server.schemas.files import DataFile
from server.schemas.run_python import QueryPythonRequest
from server.schemas.table import FilterSort, TableFilter, TablePagination, TableSort


def verify_state(app_name: str, page_name: str, state: dict):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "state": state,
    }
    return run_process_task_unwrap("verify_state", args)


def run_query(req: QueryPythonRequest):
    # read page properties
    properties = read_page_properties(req.app_name, req.page_name)
    file = get_table_data_fetcher(properties["files"], req.table.fetcher)
    file = DataFile(**file)

    if file.type == "data_fetcher":
        resp = run_python_query(
            req.app_name, req.page_name, file, req.state, req.context, req.filter_sort
        )
    else:
        resp = run_sql_query(
            req.app_name, req.page_name, file, req.state, req.filter_sort
        )
    return resp


def run_python_query(
    app_name: str,
    page_name: str,
    file: DataFile,
    state: dict,
    context: dict,
    filter_sort: FilterSort,
):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "file": file.dict(),
        "state": state,
        "context": context,
        "filter_sort": filter_sort.dict(),
    }
    return run_process_task_unwrap("run_python_query", args)


def run_sql_query(
    app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort
):
    verify_state(app_name, page_name, state)

    sql = get_sql_from_file(app_name, page_name, file.name)
    df = run_df_query(sql, file.source, state, filter_sort)

    res = convert_df_to_resp_obj(df)
    return format_process_result(res)


def run_sql_query_from_string(
    sql: str, source: str, app_name: str, page_name: str, state: dict
):
    verify_state(app_name, page_name, state)
    df = run_df_query(sql, source, state)
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
        filters=[],
        sorts=[],
        pagination=TablePagination(page=0, page_size=DATA_PREVIEW_SIZE),
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
    return apply_filters(
        sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination
    )


def clean_sql(sql):
    return sql.strip("\n ;")


def render_sql(user_sql: str, state: dict):
    env = Environment()
    template = env.from_string(user_sql)
    return template.render(state=state)


def get_sql_from_file(app_name: str, page_name: str, file_name: str) -> str:
    path = cwd + f"/workspace/{app_name}/{page_name}/scripts/{file_name}.sql"
    with open(path, "r") as sql_file:
        sql = sql_file.read()
    return sql


def get_depend_table_names(user_sql: str):
    pattern = re.compile(r"\{\{state\.tables\.(\w+)\.\w+\}\}")
    matches = pattern.findall(user_sql)
    return list(set(matches))


def query_db(sql, values, source_name):
    user_db_engine = connect_to_user_db(source_name)
    with user_db_engine.connect().execution_options(autocommit=True) as conn:
        res = conn.execute(text(sql), values).all()
    return res


def apply_filters(
    table_sql: str,
    filters: List[TableFilter],
    sorts: List[TableSort],
    pagination: TablePagination = {},
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


def get_table_columns(
    app_name: str, page_name: str, file: dict, state: dict
) -> List[str]:
    if file.get("type") == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state)["result"]
    else:
        verify_state(app_name, page_name, state)
        sql = get_sql_from_file(app_name, page_name, file.get("name"))
        df = run_df_query(
            sql, file.get("source"), state, FilterSort(filters=[], sorts=[])
        )
    return df.columns.tolist()
