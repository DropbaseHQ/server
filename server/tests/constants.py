from pathlib import Path

TEST_APP_NAME = "dropbase_test_app"
TEST_PAGE_NAME = "page1"

ROOT_PATH = Path(__file__).parent.parent.parent
WORKSPACE_PATH = ROOT_PATH.joinpath("workspace")
TEMPDIR_PATH = ROOT_PATH.joinpath(".temp")
DEMO_INIT_SQL_PATH = ROOT_PATH.joinpath("demo/init.sql")
DEMO_SNOWFLAKE_INIT_SQL_PATH = ROOT_PATH.joinpath("demo/init_snowflake.sql")
