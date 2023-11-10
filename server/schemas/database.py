from pydantic import BaseModel


class PgCreds(BaseModel):
    host: str
    database: str
    username: str
    password: str
    port: int
