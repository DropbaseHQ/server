import sys

from server.constants import cwd, DATA_PREVIEW_SIZE
from server.controllers.query import get_table_sql, run_df_query, prepare_sql
from server.controllers.utils import get_state
from server.schemas.table import FilterSort, TableFilter, TableSort, TablePagination


def get_sql_from_file(app_name: str, page_name: str, file_name: str, state: dict, filter_sort: FilterSort):
    try:
        sys.path.insert(0, cwd)
        state = get_state(app_name, page_name, state)
        filter_sort = FilterSort(**filter_sort)
        user_sql = get_table_sql(app_name, page_name, file_name)
        filter_sql, filter_values = prepare_sql(user_sql, state, filter_sort)
        return {"filter_sql": filter_sql, "filter_values": filter_values}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def get_sql_from_file_content(app_name: str, page_name: str, file_content: str, state: dict):
    try:
        sys.path.insert(0, cwd)
        state = get_state(app_name, page_name, state)
        filter_sort = FilterSort(filters=[], sorts=[], pagination=TablePagination(page=0, page_size=DATA_PREVIEW_SIZE))
        filter_sql, filter_values = prepare_sql(file_content, state, filter_sort)
        return {"filter_sql": filter_sql, "filter_values": filter_values}
    except Exception as e:
        return {"error": str(e)}
