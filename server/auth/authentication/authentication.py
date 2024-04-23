import logging
from fastapi import Depends, HTTPException, status, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import JWTDecodeError
from jwt.exceptions import InvalidSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import crud
from ..models import Workspace
from ..connect import get_db

logger = logging.getLogger(__name__)


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


def get_current_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user_id = Authorize.get_jwt_subject()
        return crud.user.get_user_by_email(db, email=current_user_id)
    except JWTDecodeError as e:
        if e.message == "Signature has expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signature has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# to get a string like this run:
# openssl rand -hex 32

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_worker_token(request: Request, db: Session = Depends(get_db)):
    worker_token = request.headers.get("dropbase-token")
    if worker_token is None:
        logger.info("Worker token is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Worker token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    target_token = crud.token.get_token_by_value(db, token=worker_token)
    if not target_token:
        logger.info("Invalid worker token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid worker token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not target_token.is_active:
        logger.info("Worker token is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Worker token is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    workspace: Workspace = crud.workspace.get(db, target_token.workspace_id)
    return workspace


# Path: server/utils/connect.py
