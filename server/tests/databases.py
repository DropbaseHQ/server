import os
import sqlite3

import pytest
import snowflake.connector

from server.tests.constants import SNOWFLAKE_TEST_CONNECTION_PARAMS


@pytest.fixture(scope="session")
def snowflake_db():
    # Connect to Snowflake
    conn = snowflake.connector.connect(**SNOWFLAKE_TEST_CONNECTION_PARAMS)

    # Create a new database for testing and use it
    test_db_name = "test_db"
    test_schema_name = "PUBLIC"

    conn.cursor().execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {test_db_name}")
    conn.cursor().execute(f"USE DATABASE {test_db_name}")
    conn.cursor().execute(f"CREATE SCHEMA IF NOT EXISTS {test_schema_name}")

    yield conn  # This allows the test to run with the connection

    conn.cursor().execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    conn.close()


@pytest.fixture(scope="session")
def sqlite_db():
    db_connection = sqlite3.connect("data.db")
    yield db_connection

    db_connection.close()
    os.remove("data.db")
