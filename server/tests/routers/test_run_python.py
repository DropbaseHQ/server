from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME


def test_run_python_string(test_client):
    # Arrange
    data = {
        "file_code": f"""import pandas as pd
from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context

def test_data_fetcher(state: State) -> pd.DataFrame:
    return pd.DataFrame(data=[[1]], columns=["x"])""",
        "test_code": "test_data_fetcher(state)",
        "state": {"tables": {"table1": {}}, "widgets": {}},
        "context": {
            "tables": {
                "table1": {"message": None, "message_type": None, "reload": False, "columns": {}}
            },
            "widgets": {},
        },
    }

    # Act
    res = test_client.post("/query/python_string", json=data)

    # Assert
    assert res.status_code == 202
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["type"] == "table"
    assert res_data["columns"] == [{"name": "x", "data_type": "int64", "display_type": "integer"}]
    assert res_data["data"] == [[1]]
