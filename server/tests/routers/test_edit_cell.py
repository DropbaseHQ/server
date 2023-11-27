from server.tests.mocks.worker.python_subprocess import mock_run_process_task


def test_edit_sql_table_req(test_client, mocker):
    # Arrange
    run_process_task = mock_run_process_task(
        True,
        {
            "result": ["updated name from trevor to rovert"],
            "errors": None,
        },
        "",
    )
    mocker.patch("server.routers.query.run_process_task", side_effect=run_process_task)

    data = {
        "edits": [
            {
                "column_name": "name",
                "old_value": "trevor",
                "new_value": "rovert",
                "row": {},
                "columns": {
                    "id": {
                        "name": "id",
                        "schema_name": "public",
                        "table_name": "users",
                        "column_name": "id",
                        "edit_keys": [],
                    },
                    "name": {
                        "name": "name",
                        "schema_name": "public",
                        "table_name": "users",
                        "column_name": "name",
                        "edit_keys": ["id"],
                    }
                }
            }
        ],
        "file": {"source": "mock_db"},
    }

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=data)

    # Assert
    assert res.status_code == 200
