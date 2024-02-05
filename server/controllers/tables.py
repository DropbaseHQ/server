from server.controllers.connect import connect_to_user_db
from server.controllers.page import get_page_state_context
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.run_sql import get_sql_from_file, render_sql
from server.controllers.utils import get_table_data_fetcher
from server.requests.dropbase_router import DropbaseRouter
from server.schemas.files import DataFile
from server.schemas.table import ConvertTableRequest


def convert_sql_table(req: ConvertTableRequest, router: DropbaseRouter):
    try:
        # get db schema
        properties = read_page_properties(req.app_name, req.page_name)
        file = get_table_data_fetcher(properties["files"], req.table.fetcher)
        file = DataFile(**file)

        user_db = connect_to_user_db(file.source)
        db_schema, gpt_schema = user_db._get_db_schema()

        # get columns
        user_sql = get_sql_from_file(req.app_name, req.page_name, file.name)
        user_sql = render_sql(user_sql, req.state)
        column_names = user_db._get_column_names()

        # get columns from file
        get_smart_table_payload = {
            "user_sql": user_sql,
            "column_names": column_names,
            "gpt_schema": gpt_schema,
            "db_schema": db_schema,
        }

        resp = router.misc.get_smart_columns(get_smart_table_payload)
        if resp.status_code != 200:
            return resp.text
        smart_cols = resp.json().get("columns")
        # NOTE: columns type in smart_cols dict (from chatgpt) is called type.
        # do not confuse it with column_type, which we use internally

        # rename type to column_type
        for column in smart_cols.values():
            column["column_type"] = column.pop("type")

        # validate columns
        validated = user_db._validate_smart_cols(smart_cols, user_sql)
        column_props = [value for name, value in smart_cols.items() if name in validated]

        for column in column_props:
            column["display_type"] = user_db._detect_col_display_type(column["column_type"].lower())

        for table in properties["tables"]:
            if table["name"] == req.table.name:
                table["smart"] = True
                table["columns"] = column_props

        # update properties
        update_properties(req.app_name, req.page_name, properties)

        # get new steate and context
        return get_page_state_context(req.app_name, req.page_name), 200

    except Exception as e:
        return str(e), 500
