from sqlalchemy.orm import Session
from ..base import CRUDBase
from ...models import App


class CRUDApp(CRUDBase[App, App, App]):
    def get_app_by_name(self, db: Session, app_name: str, workspace_id: str):
        return (
            db.query(App)
            .filter(App.name == app_name, App.workspace_id == workspace_id)
            .first()
        )


app = CRUDApp(App)
