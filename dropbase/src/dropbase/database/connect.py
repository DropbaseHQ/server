from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from dropbase.database.sources import get_sources

WORKSPACE_SOURCES = get_sources()


def connect_to_user_db(name: str):
    creds = WORKSPACE_SOURCES.get(name)
    creds_fields = creds.get("fields")

    match creds.get("type"):
        case "postgres":
            return PostgresDatabase(creds_fields.dict())
        case "pg":
            return PostgresDatabase(creds_fields.dict())
        case "mysql":
            raise Exception("MySQL not supported yet")
        case "sqlite":
            return SqliteDatabase(creds_fields.dict())
        case _:
            raise Exception(f"Database type {creds_fields.get('type')} not supported")
