# DEPRECATED: In the process of refactoring DB queries out of worker
#             processes. Please use server/controllers/query.py instead
# TODO: Migrate sync columns
# TODO: Migrate update table
# TODO: Migrate convert table
# TODO: Migrate edit cell
# TODO: Delete this file

import os
from typing import List

import pandas as pd
from jinja2 import Environment, meta
from sqlalchemy import text
from sqlalchemy.engine import Engine

from server.controllers.utils import clean_df, connect_to_user_db
from server.schemas.table import FilterSort, TableFilter, TableSort, TablePagination

cwd = os.getcwd()


def run_df_query(sql: str, source: str, state, filter_sort: FilterSort):
    sql = clean_sql(sql)
    sql = render_sql(sql, state)
    filter_sql, filter_values = apply_filters(sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination)
    res = query_db(filter_sql, filter_values, source)
    df = pd.DataFrame(res)
    df = clean_df(df)
    return df


def render_sql(user_sql: str, state):
    env = Environment()
    template = env.from_string(user_sql)
    return template.render(**state.tables.dict())


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
    user_db_engine.dispose()
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
