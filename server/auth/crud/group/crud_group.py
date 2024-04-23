from ..base import CRUDBase
from ...models import Group


class CRUDGroup(CRUDBase[Group, Group, Group]):
    pass


group = CRUDGroup(Group)
