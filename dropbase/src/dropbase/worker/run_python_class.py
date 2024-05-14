import importlib
import json
import os
import traceback

from dotenv import load_dotenv

from dropbase.helpers.utils import _dict_from_pydantic_model
from dropbase.schemas.edit_cell import EditInfo

load_dotenv()


def run(r, response):
    try:
        # get evn variables
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")
        state = json.loads(os.getenv("state"))
        action = os.getenv("action")
        resource = os.getenv("resource")
        section = os.getenv("section")
        component = os.getenv("component")

        page_path = f"workspace.{app_name}.{page_name}"
        state_context_module = importlib.import_module(page_path)
        Context = getattr(state_context_module, "Context")
        context = _dict_from_pydantic_model(Context)
        context = Context(**context)

        State = getattr(state_context_module, "State")
        state = State(**state)

        # run python script and get result
        # sample path: from workspace.class_9.page1.schema import Script
        script_path = f"workspace.{app_name}.{page_name}.page"
        page_module = importlib.import_module(script_path)
        importlib.reload(page_module)
        Page = getattr(page_module, "Page")

        page = Page(app_name, page_name, state)

        # run function
        # TODO: make actions more generalizable
        if action == "get_data":
            new_context = page.__getattribute__(resource).get(state, context)
        elif action == "update":
            edits = json.loads(os.getenv("edits"))
            for edit in edits:
                edit = EditInfo(**edit)
            new_context = page.__getattribute__(resource).update(edits)
        elif action == "delete":
            row = state.get(resource).get("columns")
            new_context = page.__getattribute__(resource).delete(row)
        elif action == "add":
            row = json.loads(os.getenv("row"))
            new_context = page.__getattribute__(resource).add(row)
        else:
            # action - on_select, on_click, on_input, on_tobble
            new_context = page.__getattribute__(resource).__getattribute__(
                f"{section}_{component}_{action}"
            )(state, context)

        response["type"] = "context"
        response["context"] = new_context.dict()
        response["message"] = "job completed"
        response["status_code"] = 200
    except Exception as e:
        # catch any error and tracebacks and send to rabbitmq
        response["type"] = "error"
        response["traceback"] = traceback.format_exc()
        response["message"] = str(e)
        response["status_code"] = 500
    finally:
        # send result to redis
        r.set(os.getenv("job_id"), json.dumps(response))
        r.expire(os.getenv("job_id"), 60)
