import importlib


def verify_state_exists(module_path: str, class_name: str, attribute_name: str) -> bool:
    try:
        module_path = module_path.replace("/", ".").rstrip(".py")

        module = importlib.import_module(module_path)

        cls = getattr(module, class_name)

        return hasattr(cls, attribute_name)

    except ImportError as e:
        print(f"Error importing module: {e}")
        return False
    except AttributeError as e:
        print(f"Error accessing class: {e}")
        return False


def verify_context_exists(module_path: str, class_name: str, attribute_name: str) -> bool:
    try:
        module_path = module_path.replace("/", ".").rstrip(".py")

        module = importlib.import_module(module_path)

        cls = getattr(module, class_name)

        return hasattr(cls, attribute_name)

    except ImportError as e:
        print(f"Error importing module: {e}")
        return False
    except AttributeError as e:
        print(f"Error accessing class: {e}")
        return False
