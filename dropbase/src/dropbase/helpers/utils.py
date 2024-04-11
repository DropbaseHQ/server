import importlib
import json
import re
from pathlib import Path

import pandas as pd


def get_function_by_name(app_name: str, page_name: str, function_name: str):
    file_module = f"workspace.{app_name}.{page_name}.scripts.{function_name}"
    scripts = importlib.import_module(file_module)
    importlib.reload(scripts)
    function = getattr(scripts, function_name)
    return function


def get_state_context(app_name: str, page_name: str, state: dict, context: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    importlib.reload(page)
    State = getattr(page, "State")
    Context = getattr(page, "Context")
    return State(**state), Context(**context)


def get_state(app_name: str, page_name: str, state: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    importlib.reload(page)
    State = getattr(page, "State")
    return State(**state)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement cleaning
    return df


def validate_column_name(column: str):
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    return False if pattern.fullmatch(column) is None else True


def get_state_context_model(app_name: str, page_name: str, model_type: str):
    module_name = f"workspace.{app_name}.{page_name}.{model_type}"
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    return getattr(module, model_type.capitalize())


def get_table_data_fetcher(files: list, fetcher_name: str):
    file_data = None
    for file in files:
        if file["name"] == fetcher_name:
            file_data = file
            break
    return file_data


def check_if_object_exists(path: str):
    return Path(path).exists()


def process_query_result(res) -> pd.DataFrame:
    df = pd.DataFrame(res)
    df = clean_df(df)
    return df


def read_page_properties(app_name: str, page_name: str):
    path = f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())
