def mock_run_process_task(success: bool, result: any, stdout: str):
    def run_process_task(*args, **kwargs):
        return {"success": success, "result": result, "stdout": stdout}
    return run_process_task