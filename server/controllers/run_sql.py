import json
import re
import traceback

from jinja2 import Environment

from dropbase.helpers.dataframe import convert_df_to_resp_obj
from dropbase.schemas.query import RunSQLRequestTask, RunSQLStringTask
from server.constants import cwd
from server.controllers.connect import connect
from server.controllers.python_subprocess import verify_state
from server.controllers.redis import r
from server.controllers.utils import get_state, process_query_result


def run_sql_query_from_string(args: RunSQLStringTask):
    response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}
    try:
        verify_state(args.app_name, args.page_name, args.state)
        # connect to user db
        user_db = connect(args.source)

        # prepare sql
        sql = clean_sql(args.file_content)
        sql = render_sql(sql, args.state)

        # query db
        res = user_db._run_query(sql, {})

        # parse pandas response
        df = process_query_result(res)
        res = convert_df_to_resp_obj(df, user_db.db_type)
        r.set(args.job_id, json.dumps(res))

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
        # NOTE: returns 200 since this error is disaplyed in studio as stdout
        response["status_code"] = 200
    finally:
        # pass
        r.set(args.job_id, json.dumps(response))


def run_sql_query(args: RunSQLRequestTask):

    response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}

    try:
        verify_state(args.app_name, args.page_name, args.state)
        user_db = connect(args.file.source)
        # get query from file
        file_sql = get_sql_from_file(args.app_name, args.page_name, args.file.name)

        # get get query string and values for sqlalchemy query
        sql = clean_sql(file_sql)

        # validate state
        state = get_state(args.app_name, args.page_name, args.state)
        col_names = re.findall("{{(state.tables.*?)}}", sql)
        for col_name in col_names:
            # eval() executes the string as python code. if column is not present, it will raise an Error
            # not sure if we need globals() here though
            eval(col_name, {"state": state})

        sql = render_sql(sql, args.state)

        filter_sql, filter_values = user_db._apply_filters(
            sql, args.filter_sort.filters, args.filter_sort.sorts, args.filter_sort.pagination
        )

        # query user db
        res = user_db._run_query(filter_sql, filter_values)
        df = process_query_result(res)

        res = convert_df_to_resp_obj(df, user_db.db_type)
        r.set(args.job_id, json.dumps(res))
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

        r.set(args.job_id, str(e))
    finally:
        r.set(args.job_id, json.dumps(response))


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
