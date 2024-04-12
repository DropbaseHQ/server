import json
import os
import traceback

from dotenv import load_dotenv

from dropbase.helpers.utils import get_function_by_name, get_state_empty_context

load_dotenv()


def run(r, response):
    try:
        # get evn variables
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")
        state = json.loads(os.getenv("state"))
        file = json.loads(os.getenv("file"))
        job_id = os.getenv("job_id")

        # get state and context
        state, context = get_state_empty_context(app_name, page_name, state)

        # run python script and get result
        file_name = get_function_by_name(app_name, page_name, file.get("name"), file.get("function"))
        args = {"state": state, "context": context}
        context = file_name(**args)

        response["type"] = "context"
        response["context"] = context.dict()
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
        r.set(job_id, json.dumps(response))
        r.expire(job_id, 60)
