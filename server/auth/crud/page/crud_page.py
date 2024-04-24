# @JON: THERE IS NO PAGE SCHEMAS FOR UPDATE/DELETE. DO WE NEED THIS CRUD?
from ...models import Page
from ..base import CRUDBase


class CRUDPage(CRUDBase[Page, Page, Page]):
    def get_page_by_name(self, db, page_name, app_id):
        return db.query(Page).filter(Page.name == page_name, Page.app_id == app_id).first()


page = CRUDPage(Page)
