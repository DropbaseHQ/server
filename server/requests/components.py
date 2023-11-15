from uuid import UUID
from typing import Optional


class ComponentRouter:
    def __init__(self, session):
        self.session = session

    def create_component(
        self, property: dict, widget_id: UUID, after: Optional[UUID], type: str
    ):
        return self.session.post(
            url=f"components/",
            json={
                "property": property,
                "widget_id": widget_id,
                "after": after,
                "type": type,
            },
        )

    def update_component(self, component_id: str, update_data: dict):
        return self.session.put(url=f"components/{component_id}", json=update_data)

    def delete_component(self, component_id: str):
        return self.session.delete(url=f"components/{component_id}")
