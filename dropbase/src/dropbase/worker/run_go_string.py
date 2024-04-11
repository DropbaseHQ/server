import json
import os
import re
import subprocess
import uuid

from dotenv import load_dotenv

load_dotenv()
# Assuming 'r' and 'response' are initialized properly elsewhere


def convert_to_brackets(match):
    matched_string = match.group(0)
    parts = matched_string.split(".")[1:]
    bracket_notation = "context" + "".join([f'["{part}"]' for part in parts])

    return bracket_notation


def write_file(file_code: str, state: dict, app_name: str, page_name: str, file_name: str = {}):
    print(6.1)
    headers = """
package main

import (
    "encoding/json"
    "fmt"
    "os"
)

var state map[string]string
var context map[string]interface{}
"""
    # Initialize context and state in Go
    context_model = {}  # This should be obtained similar to your original Python approach
    print(6.2)
    python_context = json.dumps(context_model)  # Convert context model to JSON string
    print(6.3)
    context_init = f"""func init() {{
    contextData := `{python_context}`
    json.Unmarshal([]byte(contextData), &context)
    state = map[string]string{{
    """
    print(6.4)
    # State initialization in Go
    state_init_lines = ",\n".join([f'"{k}": "{v}"' for k, v in state.items()])
    state_init = state_init_lines + "\n}\n}"
    print(6.5)
    print(state_init)
    # Combine all parts into the final Go file content
    go_code_str = headers + context_init + state_init + "\nfunc main() {\n" + file_code + "\n}\n"
    pattern = r"context(\.\w+)+"
    converted_string = re.sub(pattern, convert_to_brackets, go_code_str)
    print(6.6)
    print(go_code_str)
    print(converted_string)
    with open(file_name, "w") as f:
        f.write(converted_string)

    return converted_string


def run(r, response):
    # Similar setup as before, with adjustments for Go
    base_filename = "go_job_" + uuid.uuid4().hex
    job_id = os.getenv("job_id")
    state = json.loads(os.getenv("state") or "{}")
    app_name = os.getenv("app_name")
    page_name = os.getenv("page_name")
    go_code = os.getenv("file_code")
    directory = "temp_go_files"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    go_filename = f"{directory}/{base_filename}.go"
    try:
        # The Go environment setup and file handling remain largely unchanged
        print(6)
        write_file(go_code, state, app_name, page_name, go_filename)  # Adjust variable names as needed
        print(7)

        # In Go, compile and execute in one step using 'go run'
        run_command = f"go run {go_filename}"
        print(8)
        run_result = subprocess.run(run_command, shell=True, capture_output=True)
        print(9)

        if run_result.returncode != 0:
            print(10)
            print(run_result.stderr.decode("utf-8"))
            response["stderr"] = run_result.stderr.decode("utf-8")
            response["message"] = "Go program execution error"
            response["status_code"] = 400
            return response

        print(11)
        # Handle the output from Go program execution similarly
        response["stdout"] = run_result.stdout.decode("utf-8")
        # Update response for successful execution
        response["message"] = "Execution successful"
    except Exception as e:
        response["message"] = str(e)
        response["status_code"] = 500
    finally:
        print(12)
        # Cleanup and response handling remains the same
        os.remove(go_filename)
        # Additional cleanup if necessary
        print(13)
        r.set(job_id, json.dumps(response))
        r.expire(job_id, 60)


# Adapt the rest of your Python code to integrate with this new Go setup as needed
