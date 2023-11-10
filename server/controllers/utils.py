import copy
import glob
import importlib
import inspect
import json
import os
import sys
import ast
from pathlib import Path

import pandas as pd
from datamodel_code_generator import generate
from sqlalchemy import create_engine

from server.controllers.sources import db_type_to_class, get_sources
from server.schemas.files import DataFile
from server.schemas.table import QueryTablePayload

cwd = os.getcwd()


def call_function(fn, **kwargs):
    sig = inspect.signature(fn)
    kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return fn(**kwargs)


def find_files(directory, extension="*.py"):
    return glob.glob(os.path.join(directory, extension))


def find_functions_by_signature(
    module, *, req_param_types=[], opt_param_types=[], return_type=pd.DataFrame
):
    # Find functions returning pandas DataFrame
    pandas_functions = []
    for name, obj in vars(module).items():
        if inspect.isfunction(obj):
            req_param_types_copy = copy.deepcopy(req_param_types)
            opt_param_types_copy = copy.deepcopy(opt_param_types)
            sig = inspect.signature(obj)
            if sig.return_annotation != return_type:
                continue
            for param in sig.parameters.values():
                if param.annotation in req_param_types_copy:
                    req_param_types_copy.remove(param.annotation)
                elif param.annotation in opt_param_types_copy:
                    opt_param_types_copy.remove(param.annotation)
                else:
                    break
            else:
                if len(req_param_types_copy) == 0:
                    # all req params are satisfied
                    pandas_functions.append(name)

    return pandas_functions


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


def get_data_function_by_file(app_name: str, page_name: str, file: dict):
    # TODO: refactor this to make it more robust. get_data on each file is prone to errors
    file = DataFile(**file)
    file_name = file.name.split(".")[0]
    file_module = f"workspace.{app_name}.{page_name}.scripts.{file_name}"
    scripts = importlib.import_module(file_module)
    function = getattr(scripts, file_name)
    return function


def extract_state_context_from_payload(app_name: str, page_name: str, payload: str):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    payload = json.loads(payload)
    payload = QueryTablePayload(**payload)
    Context = getattr(page, "Context")
    State = getattr(page, "State")
    return {"context": Context(**payload.context), "state": State(**payload.state)}


def get_state_context(app_name: str, page_name: str, state: dict, context: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    State = getattr(page, "State")
    Context = getattr(page, "Context")
    return State(**state), Context(**context)


def get_state(app_name: str, page_name: str, state: dict):
    # sys.path.insert(0, cwd)
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    State = getattr(page, "State")
    return State(**state)


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.fillna("")
    return df


def handle_state_context_updates(response):
    sys.path.insert(0, cwd)
    if response.status_code == 200:
        resp = response.json()
        update_state_context_files(
            resp.get("app_name"),
            resp.get("page_name"),
            resp.get("state"),
            resp.get("context"),
        )
        return {"message": "success"}
    else:
        return {"message": "error"}


def update_state_context_files(app_name, page_name, state, context):
    try:
        generate(
            input_=json.dumps(state),
            input_file_type="json",
            output=Path(f"workspace/{app_name}/{page_name}/state.py"),
        )
        generate(
            input_=json.dumps(context),
            input_file_type="json",
            output=Path(f"workspace/{app_name}/{page_name}/context.py"),
        )
    except Exception as e:
        raise Exception(f"Error updating state and context files: {e}")


def connect_to_user_db(source_name: str):
    sources = get_sources()
    creds = sources.get(source_name)
    CredsClass = db_type_to_class.get(creds.get("type"))
    creds = CredsClass(**creds)
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{creds.username}:{creds.password}@{creds.host}:{creds.port}/{creds.database}"
    return create_engine(SQLALCHEMY_DATABASE_URL, future=True)
