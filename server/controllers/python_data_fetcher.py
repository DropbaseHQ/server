import os
import sys
import traceback
import uuid
from datetime import datetime
from multiprocessing import Process

from sqlalchemy import create_engine

from server.constants import DF_TABLES_DB, INFER_TYPE_SAMPLE_SIZE, cwd
from server.controllers.dataframe import get_column_types
from server.controllers.run_sql import apply_filters
from server.controllers.sqlite import con
from server.controllers.utils import clean_df, get_function_by_name, get_state
from server.schemas.files import DataFile
from server.schemas.run_python import QueryPythonRequest


def query_python_table(req: QueryPythonRequest, file: DataFile):
    try:
        table = req.table

        # compose df table name
        df_table_name = f"{req.app_name}_{req.page_name}_{table.name}_{req.user_id}"

        # check if table exists and is ready
        status = con.execute(
            "SELECT status, message FROM table_registry WHERE table_name = ?",
            (df_table_name,),
        ).fetchone()

        # if table doesn't exist, start task
        if not status:
            return run_data_fetcher_task(req, file, df_table_name)
        # handle pending and failed status
        if status[0] == 0:
            return {"message": "Table is still being processed"}, 202
        if status[0] == 2:
            return {"message": f"Table processing failed. Error: {status[1]}"}, 500

        base_sql = f"SELECT * FROM {df_table_name}"
        filter_sort = req.filter_sort

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
            "UPDATE table_registry SET last_used = ? WHERE table_name = ?",
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


def run_data_fetcher_task(req: QueryPythonRequest, file: DataFile, df_table_name: str):
    # create a new table version
    version = "v" + uuid.uuid4().hex
    # upsert table registry with new table version
    con.execute(
        """INSERT INTO table_registry VALUES (?, ?, ?, ?)
ON CONFLICT(table_name) DO UPDATE SET status=?, message=?, version=?;""",
        (
            df_table_name,  # table name
            0,  # status
            "pending",  # message
            version,  # version
            0,  # status
            "pending",  # message
            version,  # version
        ),
    )

    # start task
    task = Process(
        target=run_data_fetcher,
        args=(df_table_name, req.dict(), file.dict(), version),
    )
    task.start()
    return {"message": "Job has started"}, 202


def run_data_fetcher(table_name: str, req: dict, file: dict, version: str):
    # NOTE: because this runs in subprocess, it has to have its own connection
    eng = create_engine(f"sqlite:///{DF_TABLES_DB}")
    con = eng.connect()

    # Change the current working directory to root_directory
    os.chdir(cwd)
    sys.path.append(cwd)  # Append your root directory to the Python import path

    try:
        # get state
        app_name, page_name, state = req.get("app_name"), req.get("page_name"), req.get("state")
        state = get_state(app_name, page_name, state)
        args = {"state": state}
        # run user data fetcher function
        function_name = get_function_by_name(app_name, page_name, file.get("name"))
        # call function
        df = function_name(**args)
        df = clean_df(df)

        # update registry table
        added_rec = con.execute(
            """UPDATE table_registry SET status = ?, message = ?
WHERE table_name = ? and version = ? and status = 'pending' RETURNING *;""",
            (
                0,
                "writing",
                table_name,
                version,
            ),
        ).fetchone()

        if added_rec:
            # write to sqlite table
            df.to_sql(table_name, con=con, index=False, if_exists="replace")

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

            con.execute(
                """UPDATE table_registry SET status = ?, message = ?
WHERE table_name = ? and version = ? RETURNING *;""",
                (
                    1,
                    "success",
                    table_name,
                    version,
                ),
            )

    except Exception:
        # save exception to file
        exception = traceback.format_exc()  # get full exception traceback string
        con.execute(
            "UPDATE table_registry SET status = ?, message = ? WHERE table_name = ? AND version = ?;",
            (2, str(exception), table_name, version),
        )
