import ast
import importlib
import re
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


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


def get_state_context(app_name: str, page_name: str, state: dict, context: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
    State = getattr(page, "State")
    Context = getattr(page, "Context")
    return State(**state), Context(**context)


def get_state(app_name: str, page_name: str, state: dict):
    page_module = f"workspace.{app_name}.{page_name}"
    page = importlib.import_module(page_module)
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


def get_depend_table_names(user_sql: str):
    pattern = re.compile(r"\{\{state\.tables\.(\w+)\.\w+\}\}")
    matches = pattern.findall(user_sql)
    return list(set(matches))


def get_column_names(user_db_engine: Engine, user_sql: str) -> list[str]:
    if user_sql == "":
        return []
    user_sql = user_sql.strip("\n ;")
    user_sql = f"SELECT * FROM ({user_sql}) AS q LIMIT 1"
    with user_db_engine.connect().execution_options(autocommit=True) as conn:
        col_names = list(conn.execute(text(user_sql)).keys())
    return col_names


def process_query_result(res) -> pd.DataFrame:
    df = pd.DataFrame(res)
    df = clean_df(df)
    return df
