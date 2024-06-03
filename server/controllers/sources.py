# todo: group with dropbase package sources
import logging

from pydantic import ValidationError

from dropbase.schemas.database import MySQLCreds, PgCreds, SnowflakeCreds, SqliteCreds
from server.config import worker_envs

db_type_to_class = {
    "postgres": PgCreds,
    "pg": PgCreds,
    "mysql": MySQLCreds,
    "sqlite": SqliteCreds,
    "snowflake": SnowflakeCreds,
}


def get_source_name_type():
    sources = []
    databases = worker_envs.get("database", {})
    for db_type in databases:
        for key, creds in databases[db_type].items():
            try:
                # assert that the creds are valid by casting them to the appropriate class
                SourceClass = db_type_to_class.get(db_type)
                SourceClass(**creds)
                # if the creds are valid, add them to the list of sources
                sources.append({"name": key, "type": db_type})
            except ValidationError as e:
                logging.warning(f"Failed to validate source {key}.\n\nError: " + str(e))
    return sources


def get_env_vars():
    return [key for key, value in worker_envs.items() if not isinstance(value, dict)]
