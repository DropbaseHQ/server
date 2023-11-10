import subprocess


def is_valid_folder_structure(app: str = "dropbase_test_app", page: str = "page1") -> bool:
    # Calls itself, see below
    proc = subprocess.run(["python", __file__, app, page])
    return proc.returncode == 0


def _verify_page_folder_structure(app_name: str, page_name: str):
    import importlib

    try:
        page_import_path = f"workspace.{app_name}.{page_name}"
        page = importlib.import_module(page_import_path)
        required_attrs = ["State", "Context"]
        missing_attrs = [attr for attr in required_attrs if not hasattr(page, attr)]
        if missing_attrs:
            raise AttributeError(
                f"[WORKSPACE STRUCTURE] {page_import_path} is missing attributes: {', '.join(missing_attrs)}"
            )
    except ImportError as e:
        raise ImportError(f"[WORKSPACE STRUCTURE] {e}")


if __name__ == "__main__":
    # Script run in subprocess to test correctness of workspace/ folder structure
    # using Python's import system.

    # We need a subprocess because Python's import system is not guaranteed to accurately
    # reflect changes to files/folders on re-imports, even if importlib.reload is called.
    import sys
    from pathlib import Path

    root_path = Path(__file__).parent.parent.parent
    sys.path.append(str(root_path))
    _verify_page_folder_structure(sys.argv[1], sys.argv[2])
