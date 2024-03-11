from dropbase.database.connect import connect_to_user_db
from dropbase.schemas.files import DataFile
from dropbase.schemas.table import ConvertTableRequest
from server.controllers.page import get_page_state_context
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.run_sql import get_sql_from_file, render_sql
from server.controllers.utils import get_table_data_fetcher
from server.requests.dropbase_router import DropbaseRouter


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
        column_names = user_db._get_column_names(user_sql)

        # get columns from file
        get_smart_table_payload = {
            "user_sql": user_sql,
            "column_names": column_names,
            "gpt_schema": gpt_schema,
            "db_schema": db_schema,
            "db_type": user_db.db_type,
        }

        resp = router.misc.get_smart_columns(get_smart_table_payload)

        if resp.status_code != 200:
            return resp
        smart_cols = resp.json().get("columns")
        # NOTE: columns type in smart_cols dict (from chatgpt) is called type

        # rename type to data_type
        for col_dict in smart_cols:
            for column in col_dict.values():
                column["data_type"] = column.pop("type")
                column["column_type"] = user_db.db_type

        # validate columns
        validated = user_db._validate_smart_cols(smart_cols, user_sql)

        column_props_list = []
        for col_dict in smart_cols:
            filtered_dict = {name: value for name, value in col_dict.items() if name in validated}
            column_props_list.append(filtered_dict)

        for col_dict in column_props_list:
            column_details = next(iter(col_dict.values()))
            column_details["display_type"] = user_db._detect_col_display_type(
                column_details["data_type"].lower()
            )

        for table in properties["tables"]:
            if table["name"] == req.table.name:
                table["smart"] = True
                table["columns"] = column_props_list

        for table in properties["tables"]:
            new_columns = []
            for col_dict in table["columns"]:
                # Assuming each dictionary in the list has only one key, and its value is another dictionary
                column_name, column_details = next(iter(col_dict.items()))
                # Add the 'name' key to the details dictionary
                column_details["name"] = column_name
                new_columns.append(column_details)
            table["columns"] = new_columns

        # update properties
        update_properties(req.app_name, req.page_name, properties)

        # get new steate and context
        return get_page_state_context(req.app_name, req.page_name), 200

    except Exception as e:
        return str(e), 500
