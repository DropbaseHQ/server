from dotenv import load_dotenv

from server.controllers.python import run_df_function
from server.controllers.query import get_table_sql, run_df_query
from server.controllers.utils import get_state
from server.schemas.files import DataFile
from server.schemas.table import FilterSort

load_dotenv()


def _get_table_columns(app_name: str, page_name: str, file: DataFile, state):
    # pass empty filter_sort
    filter_sort = FilterSort(filters=[], sorts=[])

    if file.type == "data_fetcher":
        df = run_df_function(app_name, page_name, file, state, filter_sort)
    else:
        # TODO: generalize this get_state
        state = get_state(app_name, page_name, state)
        sql = get_table_sql(app_name, page_name, file.name)
        df = run_df_query(sql, file.source, state, filter_sort)
    return df.columns.tolist()