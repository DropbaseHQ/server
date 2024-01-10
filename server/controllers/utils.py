import ast
import functools
import importlib
import inspect
import json
import os
import re
from pathlib import Path

import pandas as pd
from datamodel_code_generator import generate
from sqlalchemy import create_engine

from server.controllers.sources import db_type_to_class, get_sources
from server.schemas.files import DataFile

cwd = os.getcwd()


def call_function(fn, **kwargs):
    sig = inspect.signature(fn)
    kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return fn(**kwargs)


def rename_function_in_file(
    file_path: str,
    old_name: str,
    new_name: str,
):
    with open(file_path, "r") as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    class FunctionRenamer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            if node.name == old_name:
                node.name = new_name
            return node

    tree = FunctionRenamer().visit(tree)

    new_code = ast.unparse(tree)

    with open(file_path, "w") as file:
        file.write(new_code)


def get_function_by_name(app_name: str, page_name: str, function_name: str):
    file_module = f"workspace.{app_name}.{page_name}.scripts.{function_name}"
    scripts = importlib.import_module(file_module)
    function = getattr(scripts, function_name)
    return function


def get_data_function_by_file(app_name: str, page_name: str, file: DataFile):
    file_module = f"workspace.{app_name}.{page_name}.scripts.{file.name}"
    scripts = importlib.import_module(file_module)
    function = getattr(scripts, file.name)
    return function


def get_state_context(app_name: str, page_name: str, state: dict, context: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    # page = importlib.reload(page)
    State = getattr(page, "State")
    Context = getattr(page, "Context")
    return State(**state), Context(**context)


def get_state(app_name: str, page_name: str, state: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    # page = importlib.reload(page)
    State = getattr(page, "State")
    return State(**state)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: implement cleaning
    return df


def update_state_context_files(app_name, page_name, state, context):
    try:
        output_state_path = Path(f"workspace/{app_name}/{page_name}/state.py")
        generate(
            input_=json.dumps(state),
            input_file_type="json",
            output=output_state_path,
        )
        output_context_path = Path(f"workspace/{app_name}/{page_name}/context.py")
        generate(
            input_=json.dumps(context),
            input_file_type="json",
            output=output_context_path,
        )
    except Exception as e:
        raise Exception(f"Error updating state and context files: {e}")


@functools.lru_cache
def connect_to_user_db(source_name: str):
    sources = get_sources()
    creds = sources.get(source_name)
    CredsClass = db_type_to_class.get(creds.get("type"))
    creds = CredsClass(**creds)
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{creds.username}:{creds.password}@{creds.host}:{creds.port}/{creds.database}"  # noqa
    return create_engine(SQLALCHEMY_DATABASE_URL, future=True)


def validate_column_name(column: str):
    pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    return False if pattern.fullmatch(column) is None else True


def get_class_properties(pydantic_model):
    model_schema = pydantic_model.schema()
    model_props = model_schema.get("properties")

    obj_props = []
    for key in model_props.keys():
        prop = model_props[key]
        prop["name"] = key
        if key in model_schema.get("required", []):
            prop["required"] = True

        if "description" in prop:
            prop["type"] = prop["description"]
            prop.pop("description")
        if "enum" in prop:
            prop["type"] = "select"
        obj_props.append(prop)

    return obj_props


def get_state_context_model(app_name: str, page_name: str, model_type: str):
    module_name = f"workspace.{app_name}.{page_name}.{model_type}"
    module = importlib.import_module(module_name)
    module = importlib.reload(module)
    return getattr(module, model_type.capitalize())


def read_page_properties(app_name: str, page_name: str):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "r") as f:
        return json.loads(f.read())


def write_page_properties(app_name: str, page_name: str, properties: dict):
    path = cwd + f"/workspace/{app_name}/{page_name}/properties.json"
    with open(path, "w") as f:
        json.dump(properties, f, indent=2)


def get_table_data_fetcher(files: list, fetcher_name: str):
    file_data = None
    for file in files:
        if file["name"] == fetcher_name:
            file_data = file
            break
    return file_data
