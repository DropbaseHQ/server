import sqlite3

from server.tests.constants import DEMO_SQLITE_INIT_SQL_PATH


def init_sqlite_db():
    conn = sqlite3.connect("demo.db")

    with open(DEMO_SQLITE_INIT_SQL_PATH, "r") as rf:  # Replace this with sqlite path
        init_sql = rf.read()

    cur = conn.cursor()  # Can't use with statement in sqlite
    for statement in init_sql.split(";"):
        if statement.strip():
            cur.execute(statement)
    conn.commit()  # Commit after executing all statements
    cur.close()
