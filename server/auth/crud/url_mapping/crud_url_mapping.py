from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import URLMapping
from ...schemas import CreateURLMapping, UpdateURLMapping


class CRUDUrlMapping(CRUDBase[URLMapping, CreateURLMapping, UpdateURLMapping]):
    def get_workspace_mappings(self, db: Session, workspace_id: str):
        return (
            db.query(URLMapping).filter(URLMapping.workspace_id == workspace_id).all()
        )


url_mapping = CRUDUrlMapping(URLMapping)
