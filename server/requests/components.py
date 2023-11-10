from typing import Optional
from uuid import UUID

from server.requests.main_request import session


def create_component(property: dict, widget_id: UUID, after: Optional[UUID], type: str):
    return session.post(
        url="components/",
        json={"property": property, "widget_id": widget_id, "after": after, "type": type},
    )


def update_component(component_id: str, update_data: dict):
    return session.put(url=f"components/{component_id}", json=update_data)


def delete_component(component_id: str):
    return session.delete(url=f"components/{component_id}")
