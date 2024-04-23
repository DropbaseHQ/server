from ..base import CRUDBase
from ...models import Policy


class CRUDPolicy(CRUDBase[Policy, Policy, Policy]):
    pass


policy = CRUDPolicy(Policy)
