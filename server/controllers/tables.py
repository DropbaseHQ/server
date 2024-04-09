import json
import re

from dropbase.helpers.utils import get_table_data_fetcher
from dropbase.schemas.files import DataFile
from dropbase.schemas.table import ConvertTableRequest
from server.controllers.connect import connect
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.redis import r
from server.controllers.run_sql import get_sql_from_file, render_sql
from server.controllers.table_utils.convert import call_gpt
from server.requests.dropbase_router import DropbaseRouter


def check_for_duplicate_columns(column_names):
    unique_columns = set()
    for name in column_names:
        if name in unique_columns:
            raise Exception(f"Duplicate column name found: {name}")
        else:
            unique_columns.add(name)


def check_banned_keywords(user_sql: str) -> bool:
    normalized_sql = re.sub(r"\s+", " ", user_sql.upper())

    # Check for the presence of 'GROUP BY' or standalone 'WITH' (for CTEs)
    if "GROUP BY" in user_sql.upper():
        raise Exception("Must remove keyword GROUP BY to convert to smart table")
    if re.search(r"\bWITH\b", normalized_sql):
        # Further refinement to exclude false positives, such as 'WITH' within strings
        if not re.search(r"'[^']*WITH[^']*'", normalized_sql):
            raise Exception("Must remove keyword WITH to convert to smart table")


def convert_sql_table(req: ConvertTableRequest, router: DropbaseRouter, job_id):
    response = {"message": "", "type": "", "status_code": 202}
    try:
        # get db schema
        properties = read_page_properties(req.app_name, req.page_name)
        file = get_table_data_fetcher(properties["files"], req.table.fetcher)
        file = DataFile(**file)

        user_db = connect(file.source)

        db_schema, gpt_schema = user_db._get_db_schema()

        # get columns
        user_sql = get_sql_from_file(req.app_name, req.page_name, file.name)
        user_sql = render_sql(user_sql, req.state)

        check_banned_keywords(user_sql)
        column_names = user_db._get_column_names(user_sql)

        check_for_duplicate_columns(column_names)

        resp = call_gpt(
            user_sql=user_sql,
            column_names=column_names,
            db_schema=db_schema,
            db_type=user_db.db_type,
        )

        if resp.status_code != 200:
            return resp
        smart_cols = resp.json().get("columns")
        # NOTE: columns type in smart_cols dict (from chatgpt) is called type

        # rename type to data_type
        for column in smart_cols.values():
            column["data_type"] = column.pop("type")
            column["column_type"] = user_db.db_type

        # validate columns
        validated = user_db._validate_smart_cols(smart_cols, user_sql)
        column_props = [
            value for name, value in smart_cols.items() if name in validated
        ]

        for column in column_props:
            column["display_type"] = user_db._detect_col_display_type(
                column["data_type"].lower()
            )

        # rereading properties
        properties = read_page_properties(req.app_name, req.page_name)

        for block in properties["blocks"]:
            if block["block_type"] == "table" and block["name"] == req.table.name:
                block["smart"] = True
                block["columns"] = column_props

        update_properties(req.app_name, req.page_name, properties)

        r.set(job_id, json.dumps(response))
        response["status_code"] = 200
        return response

    except Exception as e:
        response["message"] = str(e)
        response["type"] = "error"

        response["status_code"] = 200
    finally:
        r.set(job_id, json.dumps(response))
