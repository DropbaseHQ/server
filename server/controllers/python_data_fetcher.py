import importlib
import os
import sqlite3
import sys
import traceback
import uuid
from io import StringIO
from multiprocessing import Process

from sqlalchemy import create_engine

from server.constants import INFER_TYPE_SAMPLE_SIZE, cwd
from server.controllers.dataframe import get_column_types
from server.controllers.run_sql import apply_filters
from server.controllers.sqlite import con, cur
from server.controllers.utils import clean_df, get_function_by_name, get_state
from server.schemas.files import DataFile
from server.schemas.run_python import QueryPythonRequest
from server.schemas.table import FilterSort


def query_python_table(table_name: str, filter_sort: FilterSort):

    eng = create_engine("sqlite:///page_tables.db")
    con = eng.connect()

    # check if table exists and is ready
    status = con.execute("SELECT status FROM table_names WHERE table_name = ?", (table_name,)).fetchone()
    if not status:
        raise Exception("Table not found")
    if status[0] == 0:
        raise Exception("Table is still being processed")

    sql = f"SELECT * FROM {table_name}"

    # apply filters and pagination
    filter_sql, filter_values = apply_filters(
        sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination
    )

    # query table data
    data = con.execute(filter_sql, filter_values).fetchall()
    data = [list(row) for row in data]

    # query column types
    column_types = con.execute(
        "SELECT * FROM column_types WHERE table_name = ?",
        (table_name,),
    ).fetchall()
    columns = [{"name": row[1], "column_type": row[2], "display_type": row[3]} for row in column_types]

    # return data
    return {
        "data": data,
        "columns": columns,
    }


def run_data_fetcher_task(req: QueryPythonRequest, file: DataFile):
    # create a new table name
    table_name = "t" + uuid.uuid4().hex
    cur.execute(
        "INSERT INTO table_names VALUES (?, ?, ?)",
        (
            table_name,
            0,
            "pending",
        ),
    )
    con.commit()

    task = Process(
        target=run_data_fetcher,
        args=(table_name, req.dict(), file.dict()),
    )
    task.start()
    return {
        "table_name": table_name,
    }


def run_data_fetcher(table_name: str, req: dict, file: dict):
    # create con and cur within the function
    con = sqlite3.connect("page_tables.db")
    cur = con.cursor()

    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    importlib.invalidate_caches()

    old_stdout = sys.stdout
    redirected_output = StringIO()
    sys.stdout = redirected_output

    # random file name
    try:
        app_name, page_name, state = req.get("app_name"), req.get("page_name"), req.get("state")
        state = get_state(app_name, page_name, state)
        args = {"state": state}
        function_name = get_function_by_name(app_name, page_name, file.get("name"))
        # call function
        df = function_name(**args)
        df = clean_df(df)

        # write to sqlite table
        print("writing to sqlite table")
        df.to_sql(table_name, con=con, index=False, if_exists="replace")

        # update tables
        print("updating table_names")
        cur.execute(
            "update table_names SET status = ?, message = ? where table_name = ?;",
            (
                1,
                "success",
                table_name,
            ),
        )

        # get column types
        if len(df) > INFER_TYPE_SAMPLE_SIZE:
            df = df.sample(INFER_TYPE_SAMPLE_SIZE)
        columns = get_column_types(df)
        # insert into column_types table
        print("updating column_types")
        for column in columns:
            cur.execute(
                "INSERT INTO column_types VALUES (?, ?, ?, ?)",
                (
                    table_name,
                    column.get("name"),
                    column.get("column_type"),
                    column.get("display_type"),
                ),
            )

    except Exception:
        # save exception to file
        exception = traceback.format_exc()  # get full exception traceback string
        cur.execute(
            "update table_names SET status = ?, message = ? where table_name = ?;",
            (
                2,
                str(exception),
                table_name,
            ),
        )

    finally:
        con.commit()
        sys.stdout = old_stdout
