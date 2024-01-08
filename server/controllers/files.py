import json

from server.constants import cwd
from server.schemas.files import CreateFile


def create_file(req: CreateFile):
    try:
        # create file in a local workspace
        file_name = req.name + ".sql" if req.type == "sql" else req.name + ".py"
        path = cwd + f"/workspace/{req.app_name}/{req.page_name}/scripts/{file_name}"
        boilerplate_code = compose_boilerplate_code(req)

        with open(path, "a") as f:
            f.write(boilerplate_code)

        # update properties.json
        properties_path = cwd + f"/workspace/{req.app_name}/{req.page_name}/properties.json"
        with open(properties_path, "r") as f:
            properties = json.load(f)

        properties["files"].append({"name": req.name, "type": req.type, "source": req.source})

        with open(properties_path, "w") as f:
            json.dump(properties, f, indent=2)

        return 200, {"status": "success"}
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
    elif req.type == "python":
        return """
def function():
  print("This is a generic Python function")

"""
    else:
        return ""
