import ast
import importlib
import json
import os
import traceback
import uuid

from dotenv import load_dotenv

load_dotenv()


def run(r):

    try:
        response = {"stdout": "", "traceback": "", "message": "", "type": "", "status_code": 202}
        # read state and context
        app_name = os.getenv("app_name")
        page_name = os.getenv("page_name")
        state = json.loads(os.getenv("state"))

        python_string = os.getenv("python_string")
        line_number = int(os.getenv("line_number"))

        class_name, target_method = get_target_class(python_string, line_number)
        file_name = "f" + uuid.uuid4().hex + ".py"
        test_code = f"""{class_name.lower()} = {class_name}()
new_context = {class_name.lower()}.{target_method}(state, context)"""
        # test_code = f'new_context = script.__getattribute__("{class_name.lower()}").__getattribute__("{target_method}")(state, context)'  # noqa: E501

        write_file(python_string, test_code, state, app_name, page_name, file_name)

        # import temp file
        module_name = file_name.split(".")[0]  # this gets you "temp_file"
        module = importlib.import_module(module_name)  # this imports the module
        new_context = module.new_context  # this gets the "result" from the module

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


def get_target_class(python_string: str, line_number: int):
    parsed_code = ast.parse(python_string)
    method_definitions = []

    # Find all method (function) definitions in the code
    for node in ast.walk(parsed_code):
        if isinstance(node, ast.FunctionDef):
            method_definitions.append((node.name, node.lineno, node.col_offset))

    method_definitions.sort(key=lambda x: x[1])

    # Find the method corresponding to the given line number
    target_method = None
    for method_name, method_lineno, col_offset in reversed(method_definitions):
        if method_lineno <= line_number:
            target_method = method_name
            break

    if target_method is None:
        raise ValueError("Could not find a method corresponding to the specified line number.")

    # Retrieve the class to which this method belongs
    class_definitions = [node for node in ast.walk(parsed_code) if isinstance(node, ast.ClassDef)]
    class_name = None

    # Classes should be sorted by line number to examine their boundaries
    class_definitions.sort(key=lambda x: x.lineno)

    for class_def in reversed(class_definitions):
        if class_def.lineno < line_number:
            class_methods = [node for node in class_def.body if isinstance(node, ast.FunctionDef)]
            if any(node.name == target_method for node in class_methods):
                class_name = class_def.name
                break

    if class_name is None:
        raise ValueError("Could not find a class containing the specified method.")

    return class_name, target_method


def write_file(
    python_str: str, test_code: str, state: dict, app_name: str, page_name: str, file_name: str
):
    python_str += f"""
from dropbase.helpers.utils import _dict_from_pydantic_model


# initialize context
context = _dict_from_pydantic_model(Context)
context = Context(**context)

# initialize state
state = State(**{state})
"""

    # NOTE: not all user functions will have state and context, so wrapping in try-except
    #     python_str += """
    # from dropbase.helpers.scriptABC import ScriptABC

    # class Script(ScriptABC):
    #     def __init__(self, app_name, page_name):
    #         super().__init__(app_name, page_name)
    #         kwards = {"app_name": self.app_name, "page_name": self.page_name}
    #         for key, _ in self.properties:
    #             class_name = key.capitalize()
    #             class_ = globals()[class_name]  # Get the actual class name from globals
    #             self.__dict__[key] = class_(**kwards, name=key)"""

    #     python_str += f"""
    # script = Script("{app_name}", "{page_name}")
    # """
    python_str += test_code

    with open(file_name, "w") as f:
        f.write(python_str)
