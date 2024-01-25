from sqlalchemy import create_engine

eng = create_engine("sqlite:///page_tables.db")
con = eng.connect()


def setup_tables():
    # create table_names table
    # create column_types table
    pass


def add_column_types():
    pass
