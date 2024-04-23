from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..controllers.group import GroupController
from ..controllers.group import get_group as c_get_group
from ..models import User
from ..schemas.group import (
    AddGroupPolicyRequest,
    AddUser,
    CreateGroup,
    RemoveGroupPolicyRequest,
    RemoveUser,
    UpdateGroup,
    UpdateGroupPolicyRequest,
)
from ..authorization import RESOURCES, AuthZDepFactory, get_current_user
from ..connect import get_db

group_authorizer = AuthZDepFactory(default_resource_type=RESOURCES.WORKSPACE)

router = APIRouter(prefix="/group", tags=["group"])


@router.get("/{group_id}")
def get_group(group_id: UUID, db: Session = Depends(get_db)):
    return c_get_group(db, group_id)


@router.get("/{group_id}/users")
def get_group_users(group_id: UUID, db: Session = Depends(get_db)):
    return GroupController.get_group_users(db, group_id)


@router.post("/")
def create_group(
    request: CreateGroup,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return GroupController.create_group(db=db, request=request, user=user)


@router.put("/{group_id}")
def update_group(group_id: UUID, request: UpdateGroup, db: Session = Depends(get_db)):
    return crud.group.update_by_pk(db=db, pk=group_id, obj_in=request)


@router.delete("/{group_id}")
def delete_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return GroupController.delete_group(db=db, group_id=group_id, user=user)


@router.post("/add_user/{group_id}")
def add_user_to_group(
    group_id: UUID,
    request: AddUser,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return GroupController.add_user(
        db=db, user=user, group_id=group_id, user_id=request.user_id
    )


@router.post("/remove_user/{group_id}")
def remove_user_from_group(
    group_id: UUID,
    request: RemoveUser,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return GroupController.remove_user(
        db=db, user=user, group_id=group_id, user_id=request.user_id
    )


@router.post("/add_policies/{group_id}")
def add_policies_to_group(
    group_id: UUID, request: AddGroupPolicyRequest, db: Session = Depends(get_db)
):
    return GroupController.add_policies(db, group_id, request)


@router.post("/remove_policies/{group_id}")
def remove_policies_from_group(
    group_id: UUID, request: RemoveGroupPolicyRequest, db: Session = Depends(get_db)
):
    return GroupController.remove_policies(db, group_id, request)


@router.post("/update_policy/{group_id}")
def update_policy_from_group(
    group_id: UUID, request: UpdateGroupPolicyRequest, db: Session = Depends(get_db)
):
    return GroupController.update_policy(db, group_id, request)
