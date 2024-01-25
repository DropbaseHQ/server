from typing import List

import pandas as pd
from jinja2 import Environment
from sqlalchemy import text

from server.constants import DATA_PREVIEW_SIZE, cwd
from server.controllers.dataframe import convert_df_to_resp_obj
from server.controllers.python_subprocess import format_process_result, run_process_task_unwrap
from server.controllers.utils import connect_to_user_db, process_query_result
from server.schemas.files import DataFile
from server.schemas.query import RunSQLRequest
from server.schemas.run_python import QueryPythonRequest
from server.schemas.table import FilterSort, TableFilter, TablePagination, TableSort


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


def run_sql_query(req: QueryPythonRequest, file: DataFile):
    verify_state(req.app_name, req.page_name, req.state)

    sql = get_sql_from_file(req.app_name, req.page_name, file.name)
    df = run_df_query(sql, file.source, req.state, req.filter_sort)

    res = convert_df_to_resp_obj(df)
    return {"result": res}, 200


def run_sql_query_from_string(req: RunSQLRequest):
    verify_state(req.app_name, req.page_name, req.state)
    df = run_df_query(req.file_content, req.source, req.state)
    res = convert_df_to_resp_obj(df)
    return format_process_result(res)


def prepare_sql(user_sql: str, state: dict, filter_sort: FilterSort):
    sql = clean_sql(user_sql)
    sql = render_sql(sql, state)
    return apply_filters(sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination)


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
                    filters_list.append(f'user_query."{filter.column_name}" {filter.condition}')
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


def verify_state(app_name: str, page_name: str, state: dict):
    args = {
        "app_name": app_name,
        "page_name": page_name,
        "state": state,
    }
    return run_process_task_unwrap("verify_state", args)
