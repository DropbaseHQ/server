from ..base import CRUDBase
from ...models import Page


class CRUDPage(CRUDBase[Page, Page, Page]):
    def get_page_by_name(self, db, page_name, app_id):
        return (
            db.query(Page).filter(Page.name == page_name, Page.app_id == app_id).first()
        )


page = CRUDPage(Page)
