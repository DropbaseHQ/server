from pydantic import BaseModel


class BaseDbCreds(BaseModel):
    host: str
    drivername: str
    database: str
    username: str
    password: str


class PgCreds(BaseDbCreds):
    port: int = 5432


# Child class for MySQL credentials
class MySQLCreds(BaseDbCreds):
    port: int = 3306


class SqliteCreds(BaseModel):
    drivername: str
    host: str


class SnowflakeCreds(BaseDbCreds):
    warehouse: str
    role: str
    dbschema: str
    database: str
    username: str
    password: str
