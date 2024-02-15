import os
from pathlib import Path

TEST_APP_NAME = "dropbase_test_app"
TEST_PAGE_NAME = "page1"

ROOT_PATH = Path(__file__).parent.parent.parent
WORKSPACE_PATH = ROOT_PATH.joinpath("workspace")
TEMPDIR_PATH = ROOT_PATH.joinpath(".temp")
DEMO_INIT_SQL_PATH = ROOT_PATH.joinpath("demo/init.sql")
DEMO_SNOWFLAKE_INIT_SQL_PATH = ROOT_PATH.joinpath("demo/init_snowflake.sql")

SNOWFLAKE_TEST_CONNECTION_PARAMS = {
    "account": os.getenv("SNOWFLAKE_TEST_HOST"),
    "user": os.getenv("SNOWFLAKE_TEST_USERNAME"),
    "password": "Supercool1",
    "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_TEST_DBSCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_TEST_ROLE"),
}


SNOWFLAKE_TEST_CREDS = {
    "drivername": "snowflake",
    "host": os.getenv("SNOWFLAKE_TEST_HOST"),
    "username": os.getenv("SNOWFLAKE_TEST_USERNAME"),
    "password": "Supercool1",
    "database": os.getenv("SNOWFLAKE_TEST_DATABASE"),
    "dbschema": os.getenv("SNOWFLAKE_TEST_DBSCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_TEST_WAREHOUSE"),
    "role": os.getenv("SNOWFLAKE_TEST_ROLE"),
}
