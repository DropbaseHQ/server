import asyncio
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .. import crud
from ..authentication import get_current_user
from ..connect import get_db
from ..controllers import user as user_controller
from ..models import User
from ..permissions.casbin_utils import enforce_action

logger = logging.getLogger(__name__)


class RESOURCES:
    APP = "app"
    ROLE = "role"
    USER = "user"
    WORKSPACE = "workspace"


class ACTIONS:
    USE: str = "use"
    EDIT: str = "edit"
    OWN: str = "own"


resource_query_mapper = {
    RESOURCES.ROLE: crud.user_role,
    RESOURCES.USER: crud.user,
    RESOURCES.WORKSPACE: crud.workspace,
    RESOURCES.APP: crud.app,
}
request_action_mapper = {
    "GET": ACTIONS.USE,
    "POST": ACTIONS.EDIT,
    "PUT": ACTIONS.EDIT,
    "DELETE": ACTIONS.EDIT,
}


def verify_user_id_belongs_to_current_user(
    user_id: str,
    user: User = Depends(get_current_user),
):
    if not user_id == user.id:
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user.id} cannot access user {user_id}",
        )


class AuthZDepFactory:
    def __init__(self, default_resource_type: str):
        self.default_resource_type = default_resource_type

    @staticmethod
    def _get_resource_id_from_path_params(resource_id_accessor: str, request: Request) -> Optional[str]:
        return request.path_params.get(resource_id_accessor, None)

    @staticmethod
    def _get_resource_id_from_req_body(resource_id_accessor: str, request: Request) -> Optional[str]:
        if request.headers.get("content-type") == "application/json":
            body = asyncio.run(request.json())
            return body.get(resource_id_accessor)

        return None

    @staticmethod
    def _get_workspace_id_from_req_body(request: Request) -> Optional[str]:
        body = asyncio.run(request.json())
        return body.get("workspace_id")

    def _get_resource_id(self, resource_id_accessor: str, request: Request) -> Optional[str]:
        resource_id = None

        resource_id = self._get_resource_id_from_path_params(resource_id_accessor, request)
        if resource_id is None:
            resource_id = self._get_resource_id_from_req_body(resource_id_accessor, request)

        if resource_id is None:
            # logger.warning(
            #     f"Resource ID not found in request {request.url}. Authorization passes for now."
            # )
            return False
        return resource_id

    def _get_workspace_id(self, resource_id: str, request: Request) -> Optional[str]:
        workspace_id = None
        workspace_id = self._get_workspace_id_from_req_body(request)

        if workspace_id is None and resource_id is None:
            logger.warning(f"Workspace ID not found in request {request}. Resource ID not found either.")
            return False

    @staticmethod
    def _get_resource_workspace_id(db: Session, resource_id, resource_type):
        if resource_type in resource_query_mapper:
            crud_handler = resource_query_mapper[resource_type]
            if hasattr(crud_handler, "get_workspace_id"):
                return crud_handler.get_workspace_id(db, resource_id)
            resource = crud_handler.get(db, resource_id)
            if hasattr(resource, "workspace_id"):
                return resource.workspace_id
        return None

    def _get_enforcement_params(
        self,
        db: Session,
        request: Request,
        user: User,
        resource_type: str = None,
        action: str = None,
    ):
        if resource_type is None:
            resource_type = self.default_resource_type
        resource_id_accessor = f"{resource_type}_id"

        # We want to find the resource id so that we can find the workspace id.
        # The workspace id is used to check if the user is in the workspace and what role they are.
        resource_workspace_id = None
        resource_id = self._get_resource_id(resource_id_accessor, request)
        if resource_id is False:
            if request.headers.get("workspace-id"):
                resource_workspace_id = request.headers.get("workspace-id")
            if resource_workspace_id is None:
                resource_workspace_id = self._get_resource_id_from_req_body("workspace_id", request)
            if resource_workspace_id is None:
                return None, None, None, None
        else:
            resource_workspace_id = self._get_resource_workspace_id(db, resource_id, resource_type)

        if resource_workspace_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource {resource_id} of type {resource_type} not found",
            )

        user_role = crud.user_role.get_user_role(db, user.id, resource_workspace_id)
        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User {user.id} is not in workspace {resource_workspace_id}",
            )

        if action is None:
            action = request_action_mapper.get(request.method)

        return resource_workspace_id, resource_type, action, resource_id

    @staticmethod
    def _raise_forbidden(user: User, resource_id: str):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user.id} cannot act on resource {resource_id}",
        )

    def __call__(
        self,
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
    ):
        workspace_id, resource_type, action, resource_id = self._get_enforcement_params(
            db=db, request=request, user=user
        )
        # TODO: Remove this hack. Get endpoints need workspace_id
        if workspace_id is None:
            return True
        is_authorized = enforce_action(
            db=db,
            user_id=user.id,
            workspace_id=workspace_id,
            resource=resource_type,
            action=action,
            resource_id=resource_id,
            resource_crud=resource_query_mapper[resource_type],
        )
        if not is_authorized:
            self._raise_forbidden(user, resource_id)

    def use_params(
        self,
        resource_type: str = None,
        action: str = None,
        get_permissions: bool = False,
    ):
        """Returns a one time dependency that uses the given resource type and action."""

        def verify_user_can_act_on_resource(
            request: Request,
            db: Session = Depends(get_db),
            user: User = Depends(get_current_user),
        ):
            workspace_id, resource_type_inner, action_inner, resource_id = self._get_enforcement_params(
                db, request, user, resource_type, action
            )
            # TODO: Remove this hack. Get endpoints need workspace_id
            if workspace_id is None:
                return True
            is_authorized = enforce_action(
                db=db,
                user_id=user.id,
                workspace_id=workspace_id,
                resource=resource_type_inner,
                action=action_inner,
                resource_id=resource_id,
                resource_crud=resource_query_mapper[resource_type],
            )

            if not is_authorized:
                self._raise_forbidden(user, resource_id)
            if get_permissions:
                return user_controller.check_permissions(
                    db=db, user=user, request=request, workspace_id=workspace_id
                )
            return None

        return verify_user_can_act_on_resource
