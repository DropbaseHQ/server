from abc import ABC


# TODO: modular classes
class WidgetABC(ABC):
    def __init__(self, **kwargs):
        # todo: maybe change to pydantic model
        self.name = kwargs.get("name")
        self.app_name = kwargs.get("app_name")
        self.page_name = kwargs.get("page_name")
        self.state = kwargs.get("state")
        self.context = kwargs.get("context")