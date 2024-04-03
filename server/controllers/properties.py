import json
import logging
import os
import shutil

from dropbase.schemas.page import Properties
from server.constants import cwd
from server.controllers.generate_models import create_state_context_files
from server.controllers.utils import get_state_context_model, set_by_path

logger = logging.getLogger(__name__)


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


def read_page_properties(app_name: str, page_name: str):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def write_page_properties(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        json.dump(properties, f, indent=2)


def sync_col_visibility(app_name: str, page_name: str, context: dict):
    try:
        Context = get_state_context_model(app_name, page_name, "context")
        context = Context(**context)

        properties = read_page_properties(app_name, page_name).get("blocks")

        for block in properties:
            if block["block_type"] == "table":
                for col in block["columns"]:
                    set_by_path(context, f"{block['name']}.columns.{col['name']}.hidden", col["hidden"])

        return context
    except Exception as e:
        logger.error(f"Error syncing column visibility: {e}")
        return context
