from dropbase.database.databases.mysql import MySqlDatabase
from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.snowflake import SnowflakeDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from dropbase.database.sources import get_sources

WORKSPACE_SOURCES = get_sources()


def connect(name: str):
    creds = WORKSPACE_SOURCES.get(name)
    creds_fields = creds.get("fields")

    creds_dict = creds_fields.dict()
    schema_name = "public"

    match creds.get("type"):
        case "postgres":
            return PostgresDatabase(creds_dict, schema=schema_name)
        case "pg":
            return PostgresDatabase(creds_dict, schema=schema_name)
        case "mysql":
            return MySqlDatabase(creds_dict)
        case "snowflake":
            return SnowflakeDatabase(creds_dict, schema=schema_name)
        case "sqlite":
            return SqliteDatabase(creds_dict)
        case _:
            raise Exception(f"Database type {creds_fields.get('type')} not supported")
