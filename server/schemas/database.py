from pydantic import BaseModel


class BaseDbCreds(BaseModel):
    database: str
    username: str
    password: str

class PgCreds(BaseDbCreds):
    host: str
    port: int = 5432 

# Child class for MySQL credentials
class MySQLCreds(BaseDbCreds):
    host: str
    port: int = 3306

class SqliteCreds(BaseModel):
    host: str

class SnowflakeCreds(BaseDbCreds):
    account: str
    warehouse: str
    role: str
    dbschema: str
    database: str
    username: str
    password: str