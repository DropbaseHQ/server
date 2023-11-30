from server.constants import cwd
from server.schemas.files import CreateFile
from server.requests.dropbase_router import DropbaseRouter


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
    elif req.type == "python":
        return f"""
def function():
  print("This is a generic Python function")

"""
    else:
        return ""
