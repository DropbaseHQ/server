from datetime import datetime, timedelta

from sqlalchemy import create_engine

from server.constants import STALE_TABLE_TIMEOUT

eng = create_engine("sqlite:///page_tables.db")
con = eng.connect()


def setup_tables():
    # create table_names table
    create_table_names_sql = """CREATE TABLE IF NOT EXISTS table_names (
    table_name text PRIMARY KEY,
    status integer NOT None,
    message text NOT None,
    last_used text);"""
    con.execute(create_table_names_sql)

    # create column_types table
    create_column_type_sql = """CREATE TABLE IF NOT EXISTS column_types (
    table_name text NOT NULL,
    column_name integer NOT NULL,
    column_type text NOT NULL,
    display_type text NOT NULL);"""
    con.execute(create_column_type_sql)


def check_for_stale_tables():
    # get stale tables
    stale_tables = con.execute(
        "SELECT table_name FROM table_names WHERE last_used < ?",
        (datetime.now() - timedelta(hours=STALE_TABLE_TIMEOUT),),
    ).fetchall()
    # drop stale tables
    for table in stale_tables:
        con.execute("DROP TABLE ?", (table,))
