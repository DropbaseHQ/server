from pydantic import BaseModel


class BaseDbCreds(BaseModel):
    host: str
    drivername: str
    database: str
    username: str
    password: str


class PgCreds(BaseDbCreds):
    port: int = 5432
    drivername: str = "postgresql+psycopg2"


# Child class for MySQL credentials
class MySQLCreds(BaseDbCreds):
    port: int = 3306
    drivername: str = "mysql+pymysql"


class SqliteCreds(BaseModel):
    host: str
    drivername: str = "sqlite"


class SnowflakeCreds(BaseDbCreds):
    warehouse: str
    role: str
    dbschema: str
    database: str
    username: str
    password: str
    drivername: str = "snowflake"
