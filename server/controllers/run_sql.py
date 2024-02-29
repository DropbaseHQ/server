import json
import traceback
from multiprocessing import Pipe, Process

from jinja2 import Environment

from dropbase.database.connect import connect_to_user_db
from dropbase.helpers.dataframe import convert_df_to_resp_obj
from dropbase.schemas.query import RunSQLRequestTask, RunSQLStringRequest
from server.constants import TASK_TIMEOUT, cwd
from server.controllers.python_subprocess import format_process_result, verify_state_in_subprocess
from server.controllers.redis import r
from server.controllers.utils import process_query_result


def run_sql_query_from_string(req: RunSQLStringRequest, job_id: str):
    response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}
    try:
        verify_state(req.app_name, req.page_name, req.state)
        # connect to user db
        user_db = connect_to_user_db(req.source)
        # prepare sql
        sql = clean_sql(req.file_content)
        sql = render_sql(sql, req.state)
        # query db
        res = user_db._run_query(sql, {})
        # parse pandas response
        df = process_query_result(res)
        res = convert_df_to_resp_obj(df, user_db.db_type)
        r.set(job_id, json.dumps(res))

        response["data"] = res["data"]
        response["columns"] = res["columns"]
        response["message"] = "job completed"
        response["type"] = "table"

        response["status_code"] = 200
        return {"message": "success"}
    except Exception as e:
        response["traceback"] = traceback.format_exc()
        response["message"] = str(e)
        response["type"] = "error"

        response["status_code"] = 200
    finally:
        # pass
        r.set(job_id, json.dumps(response))


def run_sql_query(args: RunSQLRequestTask, job_id: str):

    response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}

    try:
        verify_state(args.app_name, args.page_name, args.state)
        user_db = connect_to_user_db(args.file.source)
        # get query from file
        file_sql = get_sql_from_file(args.app_name, args.page_name, args.file.name)
        # get get query string and values for sqlalchemy query
        sql = clean_sql(file_sql)
        sql = render_sql(sql, args.state)

        filter_sql, filter_values = user_db._apply_filters(
            sql, args.filter_sort.filters, args.filter_sort.sorts, args.filter_sort.pagination
        )
        # query user db
        res = user_db._run_query(filter_sql, filter_values)
        df = process_query_result(res)

        res = convert_df_to_resp_obj(df, user_db.db_type)
        r.set(job_id, json.dumps(res))
        response["data"] = res["data"]
        response["columns"] = res["columns"]
        response["message"] = "job completed"
        response["type"] = "table"

        response["status_code"] = 200

    except Exception as e:
        response["traceback"] = traceback.format_exc()
        response["message"] = str(e)
        response["type"] = "error"

        response["status_code"] = 500

        r.set(job_id, format_process_result(str(e)))
    finally:
        r.set(job_id, json.dumps(response))


# NOTE: this might need to move to db classes, not all sqls have the same end of line characters
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


def verify_state(app_name: str, page_name: str, state: dict):
    parent_conn, child_conn = Pipe()

    task = Process(
        target=verify_state_in_subprocess,
        args=(child_conn, app_name, page_name, state),
    )

    task.start()
    task.join(timeout=int(TASK_TIMEOUT))

    if task.is_alive():
        task.terminate()
        task.join()  # Join again after terminating to cleanup resources
        return False

    success = parent_conn.recv()

    return success
