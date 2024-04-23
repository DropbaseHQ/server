import secrets
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..schemas.url_mapping import CreateURLMapping, UpdateURLMapping
from ..connect import get_db

router = APIRouter(prefix="/url_mapping", tags=["url_mapping"])


@router.get("/{workspace_id}")
def get_url_mappings(workspace_id: str, db: Session = Depends(get_db)):
    return crud.url_mapping.get_workspace_mappings(db, workspace_id)


@router.post("/")
def create_url_mapping(request: CreateURLMapping, db: Session = Depends(get_db)):
    return crud.url_mapping.create(db, obj_in=request)


@router.put("/{url_mapping_id}")
def update_url_mapping(
    url_mapping_id: UUID, request: UpdateURLMapping, db: Session = Depends(get_db)
):
    return crud.url_mapping.update_by_pk(db, pk=url_mapping_id, obj_in=request)


@router.delete("/{url_mapping_id}")
def delete_url_mapping(url_mapping_id: UUID, db: Session = Depends(get_db)):
    return crud.url_mapping.remove(db, id=url_mapping_id)
