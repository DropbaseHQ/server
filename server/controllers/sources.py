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


# from sqlalchemy.engine import URL
# def get_sources():
#     sources = {}
#     env_sources = config.get("sources", {})
#     for db_type in env_sources:
#         for key, creds in env_sources[db_type].items():
#             if "schema" in creds:
#                 creds["dbschema"] = creds.pop("schema")
#             try:
#                 SourceClass = db_type_to_class.get(db_type)
#                 creds = SourceClass(**creds)
#                 sources[key] = {"creds": creds, "type": db_type}
#             except ValidationError as e:
#                 logging.warning(f"Failed to validate source {key}.\n\nError: " + str(e))
#     return sources


# def get_sources_url_type():
#     urls, types = {}, {}
#     env_sources = config.get("sources", {})
#     for db_type in env_sources:
#         for key, value in env_sources[db_type].items():
#             try:
#                 # validate the creds by casting them to the appropriate class
#                 creds = db_type_to_class.get(db_type)(**value).dict()
#                 if db_type == "sqlite":
#                     url = f"{creds['drivername']}:///{creds['host']}"
#                 elif db_type == "snowflake":
#                     query = {}
#                     for key in ["warehouse", "role", "dbschema"]:
#                         # snowflake creds have schema field, but it's also a pydantic's reserved field
#                         # so we use dbschema instead
#                         if "dbschema" in creds:
#                             query["schema"] = creds.pop("dbschema")
#                         if key in creds:
#                             query[key] = creds.pop(key)
#                     url = URL.create(query=query, **creds)
#                 else:
#                     url = URL.create(**creds)
#                 urls[key] = url
#                 types[key] = db_type
#             except Exception as e:
#                 logging.info(f"Failed parse credentials for {key}. Error: {e}")
#                 pass
#     return urls, types
