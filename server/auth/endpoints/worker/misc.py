from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...controllers.tables.convert import call_gpt, fill_smart_cols_data
from server.schemas import (
    CheckPermissionRequest,
    SyncStructureRequest,
    SyncAppRequest,
    CheckAppsPermissionsRequest,
)
from server.controllers.user import user_controller
from server.controllers import workspace as workspace_controller
from server.utils.connect import get_db
from ...models import User, Workspace
from server import crud

router = APIRouter()


class ConvertTable(BaseModel):
    user_sql: str
    column_names: list
    gpt_schema: dict
    db_schema: dict
    db_type: str


@router.post("/get_smart_cols/")
def get_smart_cols(req: ConvertTable, db: Session = Depends(get_db)):
    smart_col_paths = call_gpt(
        req.user_sql, req.column_names, req.gpt_schema, req.db_type
    )

    # Fill smart col data before validation to get
    # primary keys along with other column metadata
    return fill_smart_cols_data(smart_col_paths, req.db_schema)
