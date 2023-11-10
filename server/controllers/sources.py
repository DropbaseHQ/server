import logging

from dotenv import dotenv_values
from pydantic import ValidationError

from server.schemas.database import PgCreds

db_type_to_class = {"postgres": PgCreds, "pg": PgCreds}


def get_sources():
    config = dotenv_values(".env")
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
        SourceClass = db_type_to_class.get(source["type"])
        try:
            SourceClass(**source)
            verified_sources[name] = source
        except ValidationError as e:
            logging.warning(f"Failed to validate source {name}.\n\nError: " + str(e))
    return verified_sources
