from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from server import crud
from server.schemas.worker_status import CreateWorkerStatus
from server.utils.authorization import RESOURCES, AuthZDepFactory
from server.utils.connect import get_db

widget_authorizer = AuthZDepFactory(default_resource_type=RESOURCES.WIDGET)
router = APIRouter(prefix="/worker_status", tags=["worker_status"])


@router.get("/{token}/{version}")
def get_app(token: str, version: str, response: Response, db: Session = Depends(get_db)):
    try:
        obj_in = CreateWorkerStatus(token=token, version=version)
        crud.worker_status.create(db, obj_in=obj_in)
        return {"message": "ok"}
    except Exception as e:
        print(e)
        response.status_code = 500
        return {"message": "error"}
