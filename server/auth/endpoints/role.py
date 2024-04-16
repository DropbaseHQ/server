from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..schemas.role import CreateRole, UpdateRole
from ..authorization import RESOURCES, AuthZDepFactory
from ..connect import get_db

role_authorizer = AuthZDepFactory(default_resource_type=RESOURCES.WORKSPACE)

router = APIRouter(
    prefix="/role",
    tags=["role"],
    dependencies=[Depends(role_authorizer)],
)


@router.get("/{role_id}")
def get_role(role_id: UUID, db: Session = Depends(get_db)):
    return crud.user_role.get_object_by_id_or_404(db, id=role_id)


@router.post("/")
def create_role(request: CreateRole, db: Session = Depends(get_db)):
    return crud.user_role.create(db, obj_in=request)


@router.put("/{role_id}")
def update_role(role_id: UUID, request: UpdateRole, db: Session = Depends(get_db)):
    return crud.user_role.update_by_pk(db, pk=role_id, obj_in=request)


@router.delete("/{role_id}")
def delete_role(role_id: UUID, db: Session = Depends(get_db)):
    return crud.user_role.remove(db, id=role_id)
