import json
import os
import shutil

from dropbase.helpers.state_context import create_state_context_files
from dropbase.schemas.page import Properties
from server.constants import cwd


def update_properties(app_name: str, page_name: str, properties: dict, update_modes: bool = True):

    assert Properties(**properties)

    page_dir_path = f"workspace/{app_name}/{page_name}"
    page_dir_path_backup = f"{page_dir_path}_backup"

    # create a backup by copying entire directory (including subdirectories)
    shutil.copytree(page_dir_path, page_dir_path_backup)

    try:
        # write properties
        write_page_properties(app_name, page_name, properties)

        # update state and context models
        if update_modes:
            # update state context
            create_state_context_files(page_dir_path, properties)
    except Exception as e:
        # on failure, delete edited directory
        shutil.rmtree(page_dir_path)
        # rename backup directory to original name
        os.rename(page_dir_path_backup, page_dir_path)
        raise e
    finally:
        # if no exception occurred, you can remove the backup
        if os.path.isdir(page_dir_path_backup):
            shutil.rmtree(page_dir_path_backup)


def write_page_properties(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        json.dump(properties, f, indent=2)
