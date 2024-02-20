from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory


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


class TableContextProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]
    reload: Annotated[Optional[bool], PropertyCategory.other] = False


class TableDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    # data fetcher
    fetcher: Annotated[Optional[str], PropertyCategory.default]

    # settings
    height: Annotated[Optional[str], PropertyCategory.default]
    size: Annotated[Optional[int], PropertyCategory.default] = 10

    # actions
    # TODO: implement these
    # on_row_change: Annotated[Optional[str], PropertyCategory.events]
    # on_row_selection: Annotated[Optional[str], PropertyCategory.events]

    # table filters
    filters: Annotated[Optional[List[PinnedFilter]], PropertyCategory.other]

    # internal
    type: Optional[Literal["python", "sql"]] = "sql"
    smart: Optional[bool] = False
