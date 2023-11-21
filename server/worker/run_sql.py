import sys

from server.constants import cwd
from server.controllers.query import get_table_sql, run_df_query
from server.controllers.utils import get_state
from server.schemas.files import DataFile
from server.schemas.table import FilterSort


def run_sql_query(app_name: str, page_name: str, file: DataFile, state: dict, filter_sort: FilterSort):
    sys.path.insert(0, cwd)
    state = get_state(app_name, page_name, state)
    file = DataFile(**file)
    filter_sort = FilterSort(**filter_sort)
    sql = get_table_sql(app_name, page_name, file.name)
    df = run_df_query(sql, file.source, state, filter_sort)
    return {"columns": df.columns.tolist(), "data": df.values.tolist()}


def run_sql_from_string(app_name: str, page_name: str, file_content: str, source: str, state: dict):
    sys.path.insert(0, cwd)
    state = get_state(app_name, page_name, state)
    filter_sort = FilterSort(filters=[], sorts=[])
    df = run_df_query(file_content, source, state, filter_sort)
    return {"columns": df.columns.tolist(), "data": df.values.tolist()}
