from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from server.models.category import PropertyCategory


class Filter(BaseModel):
    column_name: str
    condition: Literal["=", ">", "<", ">=", "<=", "like", "in"]
    value: Any


class Sort(BaseModel):
    column_name: str
    value: Literal["asc", "desc"]


class PinnedFilter(BaseModel):
    column_name: str
    condition: Literal["=", ">", "<", ">=", "<=", "like", "in"]


class TableDisplayProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]
    should_reload: Annotated[Optional[bool], PropertyCategory.other] = False


class TableSharedProperty(BaseModel):
    pass


class TableContextProperty(TableDisplayProperty, TableSharedProperty):
    pass


class TableBaseProperty(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    label: Annotated[str, PropertyCategory.default]
    type: Annotated[Literal["python", "sql"], PropertyCategory.default] = "sql"

    # settings
    height: Annotated[Optional[str], PropertyCategory.default]
    size: Annotated[Optional[int], PropertyCategory.default] = 10

    # data fetcher
    fetcher: Annotated[Optional[str], PropertyCategory.default]
    depends_on: Annotated[Optional[List[str]], PropertyCategory.default]

    # actions
    on_row_change: Annotated[Optional[str], PropertyCategory.events]
    on_row_selection: Annotated[Optional[str], PropertyCategory.events]

    # table filters
    filters: Annotated[Optional[List[PinnedFilter]], PropertyCategory.other]


class TableDefinedProperty(TableBaseProperty, TableSharedProperty):
    pass
