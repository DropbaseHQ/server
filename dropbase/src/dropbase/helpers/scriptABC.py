from abc import ABC

from dropbase.helpers.utils import get_page_properties


class ScriptABC(ABC):
    """
    handles user script execution, running functions
    """

    def __init__(self, app_name: str, page_name: str):
        # set properties
        self.properties = get_page_properties(app_name, page_name)
        self.app_name = app_name
        self.page_name = page_name

    # methods that handle actions
    def reload_properties(self):
        properties = get_page_properties(self.app_name, self.page_name)
        self.properties = properties
        return self.properties
