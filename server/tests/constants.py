import os
from pathlib import Path

import toml

TEST_APP_NAME = "dropbase_test_app"
TEST_PAGE_NAME = "page1"


ROOT_PATH = Path(__file__).parent.parent.parent
WORKSPACE_PATH = ROOT_PATH.joinpath("workspace")
TEMPDIR_PATH = ROOT_PATH.joinpath(".temp")
DEMO_INIT_POSTGRESQL_PATH = ROOT_PATH.joinpath("demo/init_postgres.sql")
DEMO_INIT_MYSQL_PATH = ROOT_PATH.joinpath("demo/init_mysql.sql")
DEMO_INIT_SNOWFLAKE_PATH = ROOT_PATH.joinpath("demo/init_snowflake.sql")
DEMO_INIT_SQLITE_PATH = ROOT_PATH.joinpath("demo/init_sqlite.sql")


MYSQL_TEST_CREDS = {
    "host": "localhost",
    "database": "test",
    "username": "root",
    "password": "",
    "port": 3307,
    "drivername": "mysql+pymysql",
}


MYSQL_TEST_CONNECTION_PARAMS = {
    "host": "localhost",
    "database": "test",
    "user": "root",
    "password": "",
    "port": 3307,
}


with open("config.toml", "r") as toml_file:
    config = toml.load(toml_file)


SNOWFLAKE_TEST_CREDS = config["sources"]["snowflake"]["test"]
SNOWFLAKE_TEST_CREDS["drivername"] = "snowflake"
SNOWFLAKE_TEST_CREDS["dbschema"] = SNOWFLAKE_TEST_CREDS.pop("schema")


SNOWFLAKE_TEST_CONNECTION_PARAMS = SNOWFLAKE_TEST_CREDS.copy()
SNOWFLAKE_TEST_CONNECTION_PARAMS["account"] = SNOWFLAKE_TEST_CONNECTION_PARAMS.pop("host")
SNOWFLAKE_TEST_CONNECTION_PARAMS["user"] = SNOWFLAKE_TEST_CONNECTION_PARAMS.pop("username")
SNOWFLAKE_TEST_CONNECTION_PARAMS["schema"] = SNOWFLAKE_TEST_CONNECTION_PARAMS.pop("dbschema")


SQLITE_TEST_CONNECTION_PARAMS = {
    "database": "data.db",
}


SQLITE_TEST_CREDS = {
    "drivername": "sqlite",
    "host": "data.db",
}
