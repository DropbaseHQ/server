from dropbase.database.databases.mysql import MySqlDatabase
from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.snowflake import SnowflakeDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from dropbase.database.sources import get_sources


def connect(name: str, schema_name="public"):
    sources = get_sources()
    source = sources.get(name)
    match source.get("type"):
        case "postgres":
            return PostgresDatabase(source.get("creds"), schema=schema_name)
        case "mysql":
            return MySqlDatabase(source.get("creds"))
        case "snowflake":
            return SnowflakeDatabase(source.get("creds"), schema=schema_name)
        case "sqlite":
            return SqliteDatabase(source.get("creds"))
        case _:
            raise Exception(f"Database type {source.get('type')} not supported")
