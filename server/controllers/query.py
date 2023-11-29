import os
import json
from typing import List

import pandas as pd
from jinja2 import Environment, meta
from sqlalchemy import text
from sqlalchemy.engine import Engine

from server.constants import DATA_PREVIEW_SIZE
from server.controllers.utils import clean_df, connect_to_user_db
from server.schemas.files import DataFile
from server.schemas.table import FilterSort, TableFilter, TableSort, TablePagination
from server.worker.python_subprocess import run_process_task

cwd = os.getcwd()


# TREVOR TODO move this to validate.py
def verify_state(app_name: str, page_name: str, state: dict):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "state": state,
    }
    return run_process_task("verify_state", args)


def run_python_query(app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "file": file.dict(),
        "state": state,
        "filter_sort": filter_sort.dict()
    }
    return run_process_task("run_python_query", args)


def run_sql_query(app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort):
    resp, status_code = verify_state(app_name, page_name, state)
    if status_code == 200:
        sql = get_table_sql(app_name, page_name, file.name)
        df = run_df_query(sql, file.source, state, filter_sort)
        resp["result"] = json.loads(df.to_json(orient="split"))
    return resp, status_code


def run_sql_query_from_string(sql: str, source: str, app_name: str, page_name: str, state: dict, filter_sort: FilterSort):
    resp, status_code = verify_state(app_name, page_name, state)
    if status_code == 200:
        df = run_df_query(sql, source, state, filter_sort)
        resp["result"] = json.loads(df.to_json(orient="split"))
    return resp, status_code


def run_df_query(
    user_sql: str,
    source: str,
    state: dict,
    filter_sort: FilterSort=FilterSort(filters=[], sorts=[], pagination=TablePagination(page=0, page_size=DATA_PREVIEW_SIZE))
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


def render_sql(user_sql: str, state: dict):
    env = Environment()
    template = env.from_string(user_sql)
    return template.render(**state["tables"])


def get_sql_variables(user_sql: str):
    env = Environment()
    parsed_content = env.parse(user_sql)
    return list(meta.find_undeclared_variables(parsed_content))


def get_table_sql(app_name: str, page_name: str, file_name: str) -> str:
    path = cwd + f"/workspace/{app_name}/{page_name}/scripts/{file_name}.sql"
    with open(path, "r") as sql_file:
        sql = sql_file.read()
    return sql


def clean_sql(sql):
    return sql.strip("\n ;")


def query_db(sql, values, source_name):
    user_db_engine = connect_to_user_db(source_name)
    with user_db_engine.connect().execution_options(autocommit=True) as conn:
        res = conn.execute(text(sql), values).all()
    return res


def apply_filters(table_sql: str, filters: List[TableFilter], sorts: List[TableSort], pagination: TablePagination = {}):
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
            if filter.condition == "like":
                filter.value = f"%{filter.value}%"

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
