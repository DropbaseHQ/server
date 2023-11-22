class WidgetRouter:
    def __init__(self, session):
        self.session = session

    def create_widget(
        self, page_id: str, name: str, property: str, depends_on: str = None
    ):
        return self.session.post(
            url="widget/",
            json={
                "name": name,
                "property": property,
                "page_id": page_id,
                "depends_on": depends_on,
            },
        )

    def update_widget(self, widget_id: str, update_data: dict):
        return self.session.put(url=f"widget/{widget_id}", json=update_data)

    def delete_widget(self, widget_id: str):
        return self.session.delete(url=f"widget/{widget_id}")
