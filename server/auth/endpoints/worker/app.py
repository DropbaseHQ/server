from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from server import crud
from server.schemas import CreateAppRequest
from server.utils.connect import get_db
from server.utils.authentication import verify_worker_token
from ...models import Workspace

router = APIRouter(prefix="/app", tags=["app"])


@router.post("/")
def create_app(
    request: CreateAppRequest,
    db: Session = Depends(get_db),
    workspace: Workspace = Depends(verify_worker_token),
):
    if not request:
        raise HTTPException(status_code=400, detail="Invalid request")

    return crud.app.create(db, obj_in={**request.dict(), "workspace_id": workspace.id})


@router.delete("/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db)):
    return crud.app.remove(db, id=app_id)
