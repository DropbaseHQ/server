class ComponentRouter:
    def __init__(self, session):
        self.session = session

    def create_component(self, payload: dict):
        return self.session.post(url="components/", json=payload)

    def update_component(self, component_id: str, update_data: dict):
        return self.session.put(url=f"components/{component_id}", json=update_data)

    def delete_component(self, component_id: str):
        return self.session.delete(url=f"components/{component_id}")
