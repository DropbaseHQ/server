from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

from server.controllers.utils import connect_to_user_db


class Database:
    def __init__(self, database: str, schema: str = "public"):
        self.source = database
        self.schema = schema
        self.engine = connect_to_user_db(database)
        self.session_obj = scoped_session(sessionmaker(bind=self.engine))

    def __enter__(self):
        self.session = self.session_obj()
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()
        self.engine.dispose()

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()
        self.engine.dispose()

    def rollback(self):
        self.session.rollback()

    def update(self, table: str, keys: dict, values: dict, auto_commit: bool = False):
        value_keys = list(values.keys())
        if len(value_keys) > 1:
            set_claw = f"SET ({', '.join(value_keys)}) = (:{', :'.join(value_keys)})"
        else:
            set_claw = f"SET {value_keys[0]} = :{value_keys[0]}"
        key_keys = list(keys.keys())
        if len(key_keys) > 1:
            where_claw = f"WHERE ({', '.join(key_keys)}) = (:{', :'.join(key_keys)})"
        else:
            where_claw = f"WHERE {key_keys[0]} = :{key_keys[0]}"
        sql = f"""UPDATE {self.schema}.{table}\n{set_claw}\n{where_claw};"""
        values.update(keys)
        self.session.execute(text(sql), values)
        if auto_commit:
            self.commit()

    def insert(self, table: str, values: dict, auto_commit: bool = False):
        keys = list(values.keys())
        sql = f"""INSERT INTO {self.schema}.{table} ({', '.join(keys)})
        VALUES (:{', :'.join(keys)});"""
        self.session.execute(text(sql), values)
        if auto_commit:
            self.commit()

    def delete(self, table: str, keys: dict, auto_commit: bool = False):
        key_keys = list(keys.keys())
        if len(key_keys) > 1:
            where_claw = f"WHERE ({', '.join(key_keys)}) = (:{', :'.join(key_keys)})"
        else:
            where_claw = f"WHERE {key_keys[0]} = :{key_keys[0]}"
        sql = f"""DELETE FROM {self.schema}.{table}\n{where_claw};"""
        self.session.execute(text(sql), keys)
        if auto_commit:
            self.commit()
