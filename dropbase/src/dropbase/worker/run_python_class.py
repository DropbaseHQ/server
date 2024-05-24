import importlib
import json
import os
import traceback

from dotenv import load_dotenv

from dropbase.helpers.utils import _dict_from_pydantic_model

load_dotenv()


def run(r):

    try:
        # TODO: only return stdout and traceback in dev mode
        response = {
            "stdout": "",
            "traceback": "",
            "message": "",
            "type": "",
            "status_code": 202,
        }
        # read state and context
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")

        # get page module
        page_path = f"workspace.{app_name}.{page_name}"
        state_context_module = importlib.import_module(page_path)

        # initialize context
        Context = getattr(state_context_module, "Context")
        context = _dict_from_pydantic_model(Context)
        context = Context(**context)

        # initialize state
        state = json.loads(os.getenv("state"))
        State = getattr(state_context_module, "State")
        state = State(**state)

        # initialize page script
        script_path = f"workspace.{app_name}.{page_name}.script"
        page_module = importlib.import_module(script_path)
        importlib.reload(page_module)
        Script = getattr(page_module, "Script")
        script = Script(app_name, page_name)

        # get function specific variables
        action = os.getenv("action")
        resource = os.getenv("resource")
        section = os.getenv("section")
        component = os.getenv("component")

        if action == "get":
            new_context = script.__getattribute__(resource).get(state, context)
        elif action == "update":
            updates = json.loads(os.getenv("updates"))
            ColumnUpdate = getattr(state_context_module, resource.capitalize() + "ColumnUpdate")
            updates = [ColumnUpdate(**update) for update in updates]
            new_context = script.__getattribute__(resource).update(state, context, updates)
        elif action == "delete":
            new_context = script.__getattribute__(resource).delete(state, context)
        elif action == "add":
            row = json.loads(os.getenv("row"))
            ColumnsState = getattr(state_context_module, resource.capitalize() + "ColumnsState")
            row = ColumnsState(**row)
            new_context = script.__getattribute__(resource).add(state, context, row)
        elif action == "on_row_change":
            new_context = script.__getattribute__(resource).on_row_change(state, context)
        else:
            # action - on_select, on_click, on_input, on_tobble
            new_context = script.__getattribute__(resource).__getattribute__(
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
