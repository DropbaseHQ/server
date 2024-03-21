import json
import os
import shutil

from dropbase.schemas.page import Properties
from server.constants import cwd
from server.controllers.generate_models import create_state_context_files


def update_properties(app_name: str, page_name: str, properties: dict, update_modes: bool = True):

    assert Properties(**properties)

    page_dir_path = f"workspace/{app_name}/{page_name}"
    page_dir_path_backup = f"{page_dir_path}_backup"

    # Step 1: create a backup by copying entire directory (including subdirectories)
    shutil.copytree(page_dir_path, page_dir_path_backup)

    try:
        # write properties
        write_page_properties(app_name, page_name, properties)

        # update state and context models
        if update_modes:
            # update state context
            create_state_context_files(app_name, page_name, properties)
    except Exception as e:
        # Step 3: on failure, delete edited directory
        shutil.rmtree(page_dir_path)
        # Step 4: rename backup directory to original name
        os.rename(page_dir_path_backup, page_dir_path)
        raise e
    finally:
        # if no exception occurred, you can remove the backup
        if os.path.isdir(page_dir_path_backup):
            shutil.rmtree(page_dir_path_backup)


def read_page_properties(app_name: str, page_name: str):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def write_page_properties(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        json.dump(properties, f, indent=2)
