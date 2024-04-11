import json
import os
import re
import subprocess
import uuid

from dotenv import load_dotenv

from dropbase.helpers.utils import get_empty_context, get_state_context_model
from dropbase.worker.run_python_string import assign_last_expression

load_dotenv()
# Assuming 'r' and 'response' are initialized properly elsewhere


def convert_to_brackets(match):
    matched_string = match.group(0)
    parts = matched_string.split(".")[1:]
    bracket_notation = "context" + "".join([f'["{part}"]' for part in parts])

    return bracket_notation


def write_file(file_code: str, state: dict, app_name: str, page_name: str, file_name: str = {}):
    headers = """
#include <iostream>
#include <nlohmann/json.hpp>
#include <map>
#include <string>
"""
    print(6.0)
    context_model = get_empty_context(app_name, page_name)  # This is a Pydantic Model
    python_context = context_model.dict()  # This is a dictionary
    context_init_lines = json.dumps(python_context, indent=4)  # This is json
    context_init = f"""std::string jsonData = R"json(
    {context_init_lines})json";\nnlohmann::json context = nlohmann::json::parse(jsonData);"""

    print("python_context")
    print(python_context)
    print("context_init")
    print(context_init)
    print(6.1)
    # Convert the Python 'state' dict to a C++ map initialization string
    state_init_lines = ",\n".join([f'{{"{k}", "{v}"}}' for k, v in state.items()])
    print(state_init_lines)
    print(6.2)
    state_init = f"std::map<std::string, std::string> state = {{\n{state_init_lines}\n}};"
    print(state_init)
    print(6.3)

    # Construct the final C++ code string by combining file_code, the state and context init code, and test_code
    cpp_str = headers + "\n" + state_init + "\n\n" + context_init + "\n\n" + file_code + "\n\n"
    print(cpp_str)
    pattern = r"context(\.\w+)+"
    converted_string = re.sub(pattern, convert_to_brackets, cpp_str)
    print(converted_string)
    print(6.5)

    with open(file_name, "w") as f:
        print(6.6)
        f.write(converted_string)
        print(6.7)

    return converted_string


def run(r, response):
    job_id = os.getenv("job_id")
    print(1)

    # generate filename for temporary C++ source file and executable
    state = json.loads(os.getenv("state") or "{}")
    app_name = os.getenv("app_name")
    page_name = os.getenv("page_name")
    cpp_code = os.getenv("file_code")
    # test_code = os.getenv("test_code")
    print(2)

    # test_code = assign_last_expression(test_code)
    print(3)
    # print(test_code)

    base_filename = "cpp_job_" + uuid.uuid4().hex
    directory = "temp_cpp_files"  # Specify a directory name
    print(4)

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    cpp_filename = f"{directory}/{base_filename}.cpp"
    executable_filename = (
        f"{directory}/{base_filename}"  # Include the directory for the executable as well
    )
    print(5)
    try:
        # writing the C++ code to a file
        print(6)
        write_file(cpp_code, state, app_name, page_name, cpp_filename)
        print(7)

        # compiling the C++ code
        compile_command = f"g++ {cpp_filename} -o {executable_filename}"
        print(8)
        compilation_result = subprocess.run(compile_command, shell=True, capture_output=True)
        print(9)

        if compilation_result.returncode != 0:
            print(9.1)
            print(compilation_result.stderr.decode("utf-8"))
            response["stderr"] = compilation_result.stderr.decode("utf-8")
            response["message"] = "Compilation error"
            response["status_code"] = 400
            return response

        print(10)
        execution_result = subprocess.run(executable_filename, capture_output=True)
        print(10.1)
        result_json = execution_result.stdout.decode("utf-8")
        print(10.2)
        print(result_json)
        result = json.loads(result_json)
        context_model = get_empty_context(app_name, page_name)
        python_context = context_model.dict()
        python_context.update(result)
        print(10.3)
        print(result)
        Context = get_state_context_model(app_name, page_name, "context")
        print(10.4)
        print(Context)

        if Context(**python_context):
            response["context"] = python_context
            response["type"] = "context"
        else:
            print("its not")

        print(11)
        print(execution_result)
        response["stdout"] = execution_result.stdout.decode("utf-8")
        response["stderr"] = execution_result.stderr.decode("utf-8")
        print(12)
        if execution_result.returncode != 0:
            response["message"] = "Execution error"
            response["status_code"] = 400
            return response

        # update response for successful execution
        response["message"] = "Execution successful"
    except Exception as e:
        response["message"] = str(e)
        response["status_code"] = 500
    finally:
        print(13)
        response["status_code"] = 200
        print(14)
        print(response)
        # cleanup: remove the temporary files
        os.remove(cpp_filename)
        if os.path.exists(executable_filename):
            os.remove(executable_filename)
        print(15)

        r.set(job_id, json.dumps(response))
        print(16)
        r.expire(job_id, 60)
        print(17)
