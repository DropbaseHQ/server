from sqlalchemy import create_engine


# Potential classes
class BaseDatabase:
    def __init__(self, creds): # Make it so that the function changes based on which Cred type is given? Poly?
        self.creds = creds

    def get_engine(self):
        return create_engine(self.get_connection_url(), future=True)

class PostgresDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"postgresql+psycopg2://{self.creds.username}:{self.creds.password}@{self.creds.host}:{self.creds.port}/{self.creds.database}"

class MySQLDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"mysql+pymysql://{self.creds.username}:{self.creds.password}@{self.creds.host}:{self.creds.port}/{self.creds.database}"

class SQLiteDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"sqlite:///{self.creds.host}"

class SnowflakeDatabase(BaseDatabase):
    def get_connection_url(self):
        return f"snowflake://{self.creds.username}:{self.creds.password}@{self.creds.account}/{self.creds.database}/{self.creds.dbschema}?warehouse={self.creds.warehouse}"