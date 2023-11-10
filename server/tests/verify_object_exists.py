import copy
import subprocess


def workspace_object_exists(
    obj_name: str, path: str, app: str = "dropbase_test_app", page: str = "page1"
) -> bool:
    # Calls itself, see below
    proc = subprocess.run(["python", __file__, obj_name, path, app, page], capture_output=True)
    if proc.returncode == 0:
        return True
    else:
        print("STDOUT")
        print(proc.stdout.decode())
        print("STDERR")
        print(proc.stderr.decode())
        return False


def _verify_object_exists(obj_name: str, path: str, app_name: str, page_name: str):
    import importlib

    try:
        page_import_path = f"workspace.{app_name}.{page_name}"
        obj_schema = getattr(importlib.import_module(page_import_path), obj_name).schema()
        defs = copy.deepcopy(obj_schema["definitions"])
        attrs = path.split(".")
        for attr in attrs:
            ref = obj_schema["properties"][attr].get("$ref")
            if ref:
                ref_path = ref.split("/")[2:]
                obj_schema = defs
                for key in ref_path:
                    obj_schema = obj_schema[key]
    except ImportError as e:
        raise ImportError(f"[WORKSPACE STRUCTURE] {e}")
    except AttributeError:
        raise AttributeError(f"Object does not exist: {obj_name}.{path}")


if __name__ == "__main__":
    # Script run in subprocess to test correctness of workspace/ folder structure
    # using Python's import system.

    # We need a subprocess because Python's import system is not guaranteed to accurately
    # reflect changes to files/folders on re-imports, even if importlib.reload is called.
    import sys
    from pathlib import Path

    root_path = Path(__file__).parent.parent.parent
    sys.path.append(str(root_path))
    _verify_object_exists(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
