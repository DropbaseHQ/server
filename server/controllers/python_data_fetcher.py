import importlib
import os
import sqlite3
import sys
import traceback
import uuid
from io import StringIO
from multiprocessing import Process

from server.constants import INFER_TYPE_SAMPLE_SIZE, cwd
from server.controllers.dataframe import get_column_types
from server.controllers.utils import clean_df, get_function_by_name, get_state
from server.schemas.files import DataFile
from server.schemas.run_python import QueryPythonRequest


def query_python_table(table_name: str):
    # check if table exists and is ready
    # apply filters and pagination
    # fetch data and column types
    # return data
    pass


def run_data_fetcher_task(req: QueryPythonRequest, file: DataFile):
    from server.controllers.sqlite import con, cur

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

    # run_data_fetcher(table_name, req.dict(), file.dict())
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
