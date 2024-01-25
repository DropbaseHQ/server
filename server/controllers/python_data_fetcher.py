import os
import sys
import traceback
import uuid
from datetime import datetime
from multiprocessing import Process

from sqlalchemy import create_engine

from server.constants import INFER_TYPE_SAMPLE_SIZE, cwd
from server.controllers.dataframe import get_column_types
from server.controllers.run_sql import apply_filters
from server.controllers.sqlite import con
from server.controllers.utils import clean_df, get_function_by_name, get_state
from server.schemas.files import DataFile
from server.schemas.run_python import QueryPythonRequest


def query_python_table(req: QueryPythonRequest, file: DataFile):
    try:
        table = req.table
        filter_sort = req.filter_sort

        # if request does not have df_table, start a job
        if not table.df_table:
            return run_data_fetcher_task(req, file)

        # check if table exists and is ready
        status = con.execute(
            "SELECT status FROM table_names WHERE table_name = ?", (table.df_table,)
        ).fetchone()
        if not status:
            return run_data_fetcher_task(req, file)
        if status[0] == 0:
            return {"message": "Table is still being processed"}, 202

        base_sql = f"SELECT * FROM {table.df_table}"

        # apply filters and pagination
        filter_sql, filter_values = apply_filters(
            base_sql, filter_sort.filters, filter_sort.sorts, filter_sort.pagination
        )

        # query table data
        data = con.execute(filter_sql, filter_values).fetchall()
        data = [list(row) for row in data]

        # query column types
        column_types = con.execute(
            "SELECT * FROM column_types WHERE table_name = ?",
            (table.df_table,),
        ).fetchall()

        # convert to list of dicts
        columns = [
            {"name": row[1], "column_type": row[2], "display_type": row[3]} for row in column_types
        ]

        # update last_used flag
        con.execute(
            "UPDATE table_names SET last_used = ? WHERE table_name = ?",
            (
                str(datetime.now()),
                table.df_table,
            ),
        )

        # return data
        return {
            "result": {
                "data": data,
                "columns": columns,
            }
        }, 200
    except Exception as e:
        return {"message": f"Server error, {str(e)}"}, 500


def run_data_fetcher_task(req: QueryPythonRequest, file: DataFile):
    # create a new table name
    df_table = "t" + uuid.uuid4().hex
    con.execute(
        "INSERT INTO table_names VALUES (?, ?, ?)",
        (
            df_table,
            0,
            "pending",
        ),
    )

    # start task
    task = Process(
        target=run_data_fetcher,
        args=(df_table, req.dict(), file.dict()),
    )
    task.start()
    return {"message": "Job has started", "df_table": df_table}, 202


def run_data_fetcher(table_name: str, req: dict, file: dict):
    # NOTE: because this runs in subprocess, it has to have its own connection
    eng = create_engine("sqlite:///page_tables.db")
    con = eng.connect()

    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    try:
        app_name, page_name, state = req.get("app_name"), req.get("page_name"), req.get("state")
        state = get_state(app_name, page_name, state)
        args = {"state": state}
        function_name = get_function_by_name(app_name, page_name, file.get("name"))
        # call function
        df = function_name(**args)
        df = clean_df(df)

        # write to sqlite table
        df.to_sql(table_name, con=con, index=False, if_exists="replace")

        # update tables
        con.execute(
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
        for column in columns:
            con.execute(
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
        con.execute(
            "update table_names SET status = ?, message = ? where table_name = ?;",
            (
                2,
                str(exception),
                table_name,
            ),
        )
