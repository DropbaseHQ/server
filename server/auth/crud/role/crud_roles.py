from uuid import UUID

from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import Policy, Role
from ...schemas.role import CreateRole, UpdateRole


class CRUDRole(CRUDBase[Role, CreateRole, UpdateRole]):
    pass


role = CRUDRole(Role)
