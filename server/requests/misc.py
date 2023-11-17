from server.requests.main_request import session


def get_smart_columns(user_sql: str, column_names: list, gpt_schema: dict, db_schema: dict):
    return session.post(
        url="get_smart_cols/",
        json={
            "user_sql": user_sql,
            "column_names": column_names,
            "gpt_schema": gpt_schema,
            "db_schema": db_schema,
        },
    )


def update_smart_columns(smart_columns: list, table: dict):
    return session.post(
        url="update_smart_cols/",
        json={
            "smart_columns": smart_columns,
            "table": table,
        },
    )
