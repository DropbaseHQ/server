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
    block_type: Literal["table"] = "table"
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    # data fetcher
    fetcher: Annotated[Optional[str], PropertyCategory.default]
    widget: Annotated[Optional[str], PropertyCategory.default]

    # settings

    size: Annotated[Optional[int], PropertyCategory.default] = 10

    # actions
    # TODO: implement these
    # on_row_change: Annotated[Optional[str], PropertyCategory.events]
    # on_row_selection: Annotated[Optional[str], PropertyCategory.events]

    # table filters
    filters: Annotated[Optional[List[PinnedFilter]], PropertyCategory.other]

    # internal
    w: Annotated[Optional[int], PropertyCategory.internal]
    h: Annotated[Optional[int], PropertyCategory.internal]
    x: Annotated[Optional[int], PropertyCategory.internal]
    y: Annotated[Optional[int], PropertyCategory.internal]

    type: Optional[Literal["python", "sql"]] = "sql"
    smart: Optional[bool] = False
