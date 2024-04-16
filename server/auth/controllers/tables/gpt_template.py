from ...controllers.tables import gpt_templates as templates


def get_gpt_input(
    db_schema: dict, user_sql: str, column_names: list, db_type: str
) -> str:
    match db_type:
        case "postgres":
            return templates.get_postgres_gpt_input(db_schema, user_sql, column_names)
        case "mysql":
            return templates.get_mysql_gpt_input(db_schema, user_sql, column_names)
        case "snowflake":
            return templates.get_snowflake_gpt_input(db_schema, user_sql, column_names)
        case "sqlite":
            return templates.get_sqlite_gpt_input(db_schema, user_sql, column_names)
        case _:
            return templates.get_postgres_gpt_input(db_schema, user_sql, column_names)
