import logging
import os

from pydantic import ValidationError

from server.models.connect import MySQLDatabase, PostgresDatabase, SnowflakeDatabase, SQLiteDatabase
from server.schemas.database import MySQLCreds, PgCreds, SnowflakeCreds, SqliteCreds

db_type_to_class = {
    "postgres": PgCreds,
    "pg": PgCreds,
    "mysql": MySQLCreds,
    "sqlite": SqliteCreds,
    "snowflake": SnowflakeCreds,
}

db_type_to_driver = {
    "postgres": "postgresql+psycopg2",
    "pg": "postgresql+psycopg2",
    "mysql": "mysql+pymysql",
    "sqlite": "sqlite",
    "snowflake": "snowflake",
}

db_type_to_connection = {
    "postgres": PostgresDatabase,
    "pg": PostgresDatabase,
    "mysql": MySQLDatabase,
    "sqlite": SQLiteDatabase,
    "snowflake": SnowflakeDatabase,
}


def get_sources():
    # config = dotenv_values(".env")
    config = {key: os.getenv(key) for key in os.environ.keys()}
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
        source["drivername"] = db_type_to_driver.get(source["type"])
        SourceClass = db_type_to_class.get(source["type"])
        try:
            SourceClass(**source)
            """
            For now, the "name" is the unique identifier, which means there can not be classes of
            the same name, even if they are of different types
            """
            verified_sources[name] = source
        except ValidationError as e:
            logging.warning(f"Failed to validate source {name}.\n\nError: " + str(e))
    return verified_sources
