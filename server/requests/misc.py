from server.requests.main_request import session


def sync_table_columns(app_name: str, page_name: str, table_columns: dict, token: str, table_type: str):
    return session.post(
        url="sync/columns/",
        json={
            "app_name": app_name,
            "page_name": page_name,
            "table_columns": table_columns,
            "token": token,
            "table_type": table_type,
        },
    )


def sync_components(app_name: str, page_name: str, token: str):
    return session.post(
        url="sync/components/",
        json={
            "app_name": app_name,
            "page_name": page_name,
            "token": token,
        },
    )


def sync_page(page_id: str):
    return session.put(url=f"sync/page/{page_id}")


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
