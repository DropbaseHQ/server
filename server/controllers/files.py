import glob
import importlib
import os

import pandas as pd

from server import requests as dropbase_router
from server.constants import cwd
from server.controllers.utils import find_functions_by_signature
from server.schemas.files import CreateFile
from server.requests.dropbase_router import DropbaseRouter


def get_function_by_return_type(app_name, page_name, return_type):
    # find which class to look for based on return type
    req_param_models, opt_param_models, return_model = get_signature_models(
        app_name, page_name, return_type
    )

    # get and filter out files
    dir_path = cwd + f"/workspace/{app_name}/{page_name}/scripts"
    module_path = f"workspace.{app_name}.{page_name}.scripts"

    table_functions = []
    python_files = glob.glob(f"{dir_path}/*.py")

    for py_file in python_files:
        if os.path.isfile(py_file) and not py_file.endswith("__init__.py"):
            script_name = os.path.splitext(os.path.basename(py_file))[0]
            module = importlib.import_module(module_path + "." + script_name)
            pandas_functions = find_functions_by_signature(
                module,
                req_param_types=req_param_models,
                opt_param_types=opt_param_models,
                return_type=return_model,
            )
            table_functions.extend(pandas_functions)
    return table_functions


def get_signature_models(app_name, page_name, return_type) -> (list, any):
    state_module_name = f"workspace.{app_name}.{page_name}.state"
    state_module = importlib.import_module(state_module_name)
    if return_type == "context":
        context_module_name = f"workspace.{app_name}.{page_name}.context"
        context_module = importlib.import_module(context_module_name)
        # parameters must be State and Context
        req_param_models = [getattr(context_module, "Context")]
        opt_param_models = [getattr(state_module, "State")]
        return_model = getattr(context_module, "Context")
    elif return_type == "pandas":
        # parameters must be State
        req_param_models = []
        opt_param_models = [getattr(state_module, "State")]
        return_model = pd.DataFrame
    return req_param_models, opt_param_models, return_model


def create_file(req: CreateFile, router: DropbaseRouter):
    try:
        resp = router.file.create_file(req.dict())
        if resp.status_code == 200:
            file_name = req.name + ".sql" if req.type == "sql" else req.name + ".py"
            path = (
                cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
            )
            boilerplate_code = compose_boilerplate_code(req)

            with open(path, "a") as f:
                f.write(boilerplate_code)

            return 200, resp.json()
        else:
            return 400, resp.json()
    except Exception as e:
        return 500, str(e)


def compose_boilerplate_code(req: CreateFile):
    if req.type == "ui":
        return f"""from workspace.{req.app_name}.{req.page_name} import Context, State\n\n
def {req.name}(state: State, context: Context) -> Context:
    context.widgets.widget1.message = "Hello World"
    return context
"""
    elif req.type == "data_fetcher":
        return f"""from workspace.{req.app_name}.{req.page_name} import State
import pandas as pd\n\n
def {req.name}(state: State) -> pd.DataFrame:
    df = pd.DataFrame()
    return df
"""
    else:
        return ""
