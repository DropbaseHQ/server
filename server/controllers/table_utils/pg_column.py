from typing import Optional

from pydantic import BaseModel


class SqlSmartColumnProperty(BaseModel):
    # This is now compatible with all types of db's

    name: str
    type: Optional[str]

    schema_name: Optional[str]
    database_name: Optional[str]
    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    visible: bool = True
    editable: bool = False
