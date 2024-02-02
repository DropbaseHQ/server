from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Potential classes
class BaseDatabase(ABC):
    def __init__(self, creds_dict, creds):
        self.creds_dict = creds_dict
        self.creds = creds

    @abstractmethod
    def get_connection_url(self):
        pass

    def get_engine(self):
        return create_engine(self.get_connection_url(), future=True)


class PostgresDatabase(BaseDatabase):
    def get_connection_url(self):
        return URL.create(**self.creds_dict)


class MySQLDatabase(BaseDatabase):
    def get_connection_url(self):
        return URL.create(**self.creds_dict)


class SQLiteDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"sqlite:///{self.creds.host}"


class SnowflakeDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"snowflake://{self.creds.username}:{self.creds.password}@{self.creds.host}/{self.creds.database}/{self.creds.dbschema}?warehouse={self.creds.warehouse}"
