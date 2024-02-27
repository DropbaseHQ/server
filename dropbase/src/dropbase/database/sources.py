import logging
import os

from dotenv import load_dotenv
from pydantic import ValidationError

from dropbase.schemas.database import MySQLCreds, PgCreds, SnowflakeCreds, SqliteCreds

load_dotenv()


db_type_to_class = {
    "postgres": PgCreds,
    "pg": PgCreds,
    "mysql": MySQLCreds,
    "sqlite": SqliteCreds,
    "snowflake": SnowflakeCreds,
}


def get_sources():
    config = {key: os.environ.get(key) for key in os.environ.keys()}
    sources = {}
    for key, value in config.items():
        if key.startswith("SOURCE"):
            _, type, name, field = key.lower().split("_")
            if name in sources:
                sources[name][field] = value
            else:
                sources[name] = {field: value, "type": type}

    verified_sources = {}
    for name, source in sources.items():
        db_type = source["type"]
        SourceClass = db_type_to_class.get(source["type"])

        try:
            source = SourceClass(**source)
            """
            NOTE: For now, the "name" is the unique identifier, which means there can not be classes of
            the same name, even if they are of different types
            """
            verified_sources[name] = {"fields": source, "type": db_type}
        except ValidationError as e:
            logging.warning(f"Failed to validate source {name}.\n\nError: " + str(e))
    return verified_sources
