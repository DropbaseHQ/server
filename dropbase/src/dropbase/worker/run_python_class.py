import importlib
import json
import os
import traceback

from dotenv import load_dotenv

load_dotenv()


def run(r, response):
    try:
        # get evn variables
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")
        state = json.loads(os.getenv("state"))
        action = os.getenv("action")
        target = os.getenv("target")

        # run python script and get result
        # sample path: from workspace.class_9.page1.schema import Script
        script_path = f"workspace.{app_name}.{page_name}.schema"
        page_module = importlib.import_module(script_path)
        importlib.reload(page_module)
        Script = getattr(page_module, "Script")

        script = Script(app_name, page_name, state)

        # run function
        # TODO: make actions more generalizable
        if action == "get_table_data":
            new_context = script.__getattribute__(target).__getattribute__("get_table_data")()
        else:
            new_context = script.__getattribute__(action)(target)

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
