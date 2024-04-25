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
    sources = {}
    env_sources = os.environ.get("sources", "{}")
    env_sources = json.loads(env_sources)

    for db_type in env_sources:
        for key, value in env_sources[db_type].items():
            value["type"] = db_type

            if "schema" in value:
                value["dbschema"] = value.pop("schema")

            sources[key] = value

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
