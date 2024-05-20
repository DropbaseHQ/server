import json
import logging
import os

from pydantic import ValidationError

from dropbase.schemas.database import MySQLCreds, PgCreds, SnowflakeCreds, SqliteCreds

db_type_to_class = {
    "postgres": PgCreds,
    "pg": PgCreds,
    "mysql": MySQLCreds,
    "sqlite": SqliteCreds,
    "snowflake": SnowflakeCreds,
}


def get_sources():
    # get sources from environment variable
    env_sources = os.environ.get("sources", "{}")
    env_sources = json.loads(env_sources)

    sources = {}
    for db_type in env_sources:
        for name, creds in env_sources[db_type].items():
            try:
                # in this step, we both validate and ingest additional fields to the creds
                SourceClass = db_type_to_class.get(db_type)
                creds = SourceClass(**creds)
                # add to sources
                sources[name] = {"creds": creds.dict(), "type": db_type}
            except ValidationError as e:
                logging.warning(f"Failed to validate source {name}.\n\nError: " + str(e))
    return sources
