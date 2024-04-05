import json
import os
import subprocess
import uuid

from dotenv import load_dotenv

load_dotenv()
# Assuming 'r' and 'response' are initialized properly elsewhere


def run(r, response):
    job_id = os.getenv("job_id")

    # generate filename for temporary C++ source file and executable
    cpp_code = os.getenv("file_code")
    base_filename = "cpp_job_" + uuid.uuid4().hex
    directory = "temp_cpp_files"  # Specify a directory name

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    cpp_filename = f"{directory}/{base_filename}.cpp"
    executable_filename = (
        f"{directory}/{base_filename}"  # Include the directory for the executable as well
    )
    try:
        # writing the C++ code to a file
        with open(cpp_filename, "w") as cpp_file:
            cpp_file.write(cpp_code)

        # compiling the C++ code
        compile_command = f"g++ {cpp_filename} -o {executable_filename}"
        compilation_result = subprocess.run(compile_command, shell=True, capture_output=True)

        if compilation_result.returncode != 0:
            response["stderr"] = compilation_result.stderr.decode("utf-8")
            response["message"] = "Compilation error"
            response["status_code"] = 400
            return response

        execution_result = subprocess.run(executable_filename, capture_output=True)

        response["stdout"] = execution_result.stdout.decode("utf-8")
        response["stderr"] = execution_result.stderr.decode("utf-8")

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
        response["status_code"] = 200
        # cleanup: remove the temporary files
        os.remove(cpp_filename)
        if os.path.exists(executable_filename):
            os.remove(executable_filename)

        r.set(job_id, json.dumps(response))
        r.expire(job_id, 60)
