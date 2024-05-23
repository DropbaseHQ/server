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

        # load state and context
        # page_path = f"workspace.{app_name}.{page_name}"
        # state_context_module = importlib.import_module(page_path)
        # importlib.reload(state_context_module)
        # init state
        # State = getattr(state_context_module, "State")
        # state = State(**state)
        # TODO: Figure out why this is invalid for edit cells (temporarily commented out)
        # init context
        # Context = getattr(state_context_module, "Context")
        # context = _dict_from_pydantic_model(Context)
        # context = Context(**context)

        # set state and context
        # self.state = state
        # self.context = context

    # methods that handle actions
    def reload_properties(self):
        properties = get_page_properties(self.app_name, self.page_name)
        self.properties = properties
        return self.properties
