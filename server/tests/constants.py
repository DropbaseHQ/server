import os
from pathlib import Path

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

SNOWFLAKE_TEST_CREDS = {
    "drivername": "snowflake",
    "host": os.getenv("SNOWFLAKE_TEST_HOST"),
    "username": os.getenv("SNOWFLAKE_TEST_USERNAME"),
    "password": os.getenv("SNOWFLAKE_TEST_PASSWORD"),
    "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
    "dbschema": os.getenv("SNOWFLAKE_TEST_DBSCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_TEST_ROLE"),
}

# why do we need this?
SNOWFLAKE_TEST_CONNECTION_PARAMS = {
    "account": os.getenv("SNOWFLAKE_TEST_HOST"),
    "user": os.getenv("SNOWFLAKE_TEST_USERNAME"),
    "password": os.getenv("SNOWFLAKE_TEST_PASSWORD"),
    "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_TEST_DBSCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_TEST_ROLE"),
}


SNOWFLAKE_TEST_CREDS = {
    "drivername": "snowflake",
    "host": os.getenv("SNOWFLAKE_TEST_HOST"),
    "username": os.getenv("SNOWFLAKE_TEST_USERNAME"),
    "password": os.getenv("SNOWFLAKE_TEST_PASSWORD"),
    "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
    "dbschema": os.getenv("SNOWFLAKE_TEST_DBSCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_TEST_ROLE"),
}

SQLITE_TEST_CONNECTION_PARAMS = {
    "database": "data.db",
}

SQLITE_TEST_CREDS = {
    "drivername": "sqlite",
    "host": "data.db",
}
