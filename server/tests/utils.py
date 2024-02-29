import sqlite3

import psycopg2
import pymysql
import snowflake.connector

from dropbase.database.databases.mysql import MySqlDatabase
from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.snowflake import SnowflakeDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from server.tests.constants import (
    DEMO_INIT_MYSQL_PATH,
    DEMO_INIT_POSTGRESQL_PATH,
    DEMO_INIT_SNOWFLAKE_PATH,
    DEMO_INIT_SQLITE_PATH,
)


# Setup pytest-postgresql db with test data
def load_test_db(db_type="postgres", **kwargs):
    if db_type == "postgres":
        conn = psycopg2.connect(**kwargs)
    elif db_type == "mysql":
        conn = pymysql.connect(**kwargs)
    elif db_type == "snowflake":
        conn = snowflake.connector.connect(**kwargs)
    elif db_type == "sqlite":
        conn = sqlite3.connect(**kwargs)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    if db_type == "postgres":
        with open(DEMO_INIT_POSTGRESQL_PATH, "r") as rf:
            init_sql = rf.read()
    elif db_type == "snowflake":
        with open(DEMO_INIT_SNOWFLAKE_PATH, "r") as rf:
            init_sql = rf.read()
    elif db_type == "sqlite":
        with open(DEMO_INIT_SQLITE_PATH, "r") as rf:
            init_sql = rf.read()
    else:
        with open(DEMO_INIT_MYSQL_PATH, "r") as rf:
            init_sql = rf.read()

    if db_type == "sqlite":
        cur = conn.cursor()  # Can't use with statement in sqlite
        for statement in init_sql.split(";"):
            if statement.strip():
                cur.execute(statement)
    else:
        with conn.cursor() as cur:
            if db_type == "mysql":
                # MySQL might require splitting and executing each statement separately
                for statement in init_sql.split(";"):
                    if statement.strip():
                        cur.execute(statement)
            elif db_type == "snowflake":
                for statement in init_sql.split(";"):
                    if statement.strip():
                        cur.execute(statement)
            else:
                cur.execute(init_sql)
            conn.commit()


def connect_to_test_db(db_type: str, creds: dict):
    # utility function to assist in creating the db instance
    match db_type:
        case "postgres":
            return PostgresDatabase(creds, schema="public")
        case "pg":
            return PostgresDatabase(creds, schema="public")
        case "mysql":
            return MySqlDatabase(creds)
        case "snowflake":
            return SnowflakeDatabase(creds)
        case "sqlite":
            return SqliteDatabase(creds)
