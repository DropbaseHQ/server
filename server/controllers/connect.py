from server.constants import WORKSPACE_SOURCES
from server.controllers.databases.postgres import PostgresDatabase


def connect_to_user_db(name: str):
    creds = WORKSPACE_SOURCES.get(name)
    match creds.get("type"):
        case "postgres":
            return PostgresDatabase(creds.dict())
        case "mysql":
            raise Exception("MySQL not supported yet")
        case _:
            raise Exception(f"Database type {creds.get('type')} not supported")
