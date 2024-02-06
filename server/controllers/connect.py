from server.constants import WORKSPACE_SOURCES
from server.controllers.databases.mysql import MySqlDatabase
from server.controllers.databases.postgres import PostgresDatabase


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
        case _:
            raise Exception(f"Database type {creds_fields.get('type')} not supported")
