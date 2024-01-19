import importlib


def verify_object_in_state_context(
    class_name: str,
    attribute_name: str,
    is_context: bool = False,
    app_name: str = "dropbase_test_app",
    page_name: str = "page1",
) -> bool:
    file_name = "context" if is_context else "state"

    try:
        module = importlib.import_module(f"workspace.{app_name}.{page_name}.{file_name}")
        cls = getattr(module, class_name)
        return attribute_name in cls.__fields__

    except ImportError as e:
        print(f"Error importing module: {e}")
        return False
    except AttributeError as e:
        print(f"Error accessing class: {e}")
        return False
