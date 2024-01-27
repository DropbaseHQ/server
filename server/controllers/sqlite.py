import asyncio
import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine

from server.constants import DF_TABLES_DB, STALE_TABLE_TIMEOUT

eng = create_engine(f"sqlite:///{DF_TABLES_DB}")
con = eng.connect()


def setup_tables():
    # create table_registry table
    create_table_registry_sql = """CREATE TABLE IF NOT EXISTS table_registry (
    table_name text PRIMARY KEY,
    status integer NOT NULL,
    message text NOT NULL,
    version text,
    last_used text);"""
    con.execute(create_table_registry_sql)

    # create column_types table
    create_column_type_sql = """CREATE TABLE IF NOT EXISTS column_types (
    table_name text NOT NULL,
    column_name integer NOT NULL,
    column_type text NOT NULL,
    display_type text NOT NULL);"""
    con.execute(create_column_type_sql)


def delete_sqlite_database():
    con.close()
    eng.dispose()
    # delete database file
    os.remove(DF_TABLES_DB)


async def prune_stale_tables():
    while True:
        # prune sqlite database here
        print("Pruning sqlite database...")
        check_for_stale_tables()
        await asyncio.sleep(5 * 60)  # task runs every 5 minutes


def check_for_stale_tables():
    # get stale tables
    stale_tables = con.execute(
        "SELECT table_name FROM table_registry WHERE last_used < ?",
        (datetime.now() - timedelta(hours=STALE_TABLE_TIMEOUT),),
    ).fetchall()
    # clean dropbase tables
    for table in stale_tables:
        con.execute("DROP TABLE ?", (table,))
        con.execute("DELETE FROM table_registry WHERE table_name = ?", (table,))
        con.execute("DELETE FROM column_types WHERE table_name = ?", (table,))
