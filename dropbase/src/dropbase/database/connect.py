from dropbase.database.databases.mysql import MySqlDatabase
from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.snowflake import SnowflakeDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from dropbase.database.sources import get_sources

WORKSPACE_SOURCES = get_sources()


def connect_to_user_db(name: str):
    creds = WORKSPACE_SOURCES.get(name)
    creds_fields = creds.get("fields")

    schema_name = "public"

    match creds.get("type"):
        case "postgres":
            return PostgresDatabase(creds_fields.dict(), schema=schema_name)
        case "pg":
            return PostgresDatabase(creds_fields.dict(), schema=schema_name)
        case "mysql":
            return MySqlDatabase(creds_fields.dict())
        case "snowflake":
            return SnowflakeDatabase(creds_fields.dict())
        case "sqlite":
            return SqliteDatabase(creds_fields.dict())
        case _:
            raise Exception(f"Database type {creds_fields.get('type')} not supported")
