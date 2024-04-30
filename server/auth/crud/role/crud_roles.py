from ...models import Role
from ...schemas.role import CreateRole, UpdateRole
from ..base import CRUDBase


class CRUDRole(CRUDBase[Role, CreateRole, UpdateRole]):
    pass


role = CRUDRole(Role)
