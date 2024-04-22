import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from .. import crud
from ..schemas.token import CreateToken, UpdateTokenInfo
from ..connect import get_db

router = APIRouter(prefix="/token", tags=["token"])

# TODO add auth


@router.post("/")
def create_token(request: CreateToken, db: Session = Depends(get_db)):
    request.token = secrets.token_urlsafe(32)
    if request.name is None:
        tokens = crud.token.get_user_tokens_in_workspace(db, request.workspace_id)
        request.name = f"Token {len(tokens) + 1}"
    return crud.token.create(db, obj_in=request)


@router.get("/{workspace_id}/{user_id}")
def get_user_tokens_in_workspace(
    workspace_id: UUID, user_id: UUID, db: Session = Depends(get_db)
):
    return crud.token.get_user_tokens_in_workspace(db, workspace_id)


@router.get("/{token}")
def verify_token(token: str, response: Response, db: Session = Depends(get_db)):
    token = crud.token.get_token_by_value(db, token=token)
    if not token:
        response.status_code = 404
        return {"message": "Invalid token"}
    return {"message": "Token is valid"}


@router.put("/{token_id}")
def update_token(
    token_id: UUID, request: UpdateTokenInfo, db: Session = Depends(get_db)
):
    return crud.token.update_by_pk(
        db, pk=token_id, obj_in=request.dict(exclude_unset=True)
    )


@router.delete("/{token_id}")
def delete_token(token_id: UUID, db: Session = Depends(get_db)):
    return crud.token.remove(db, id=token_id)
