def test_edit_sql_table_req(test_client, mocker):
    # FIXME mocks do not persist in worker runs
    return
    # Arrange
    mocker.patch("server.controllers.utils.connect_to_user_db")

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
    print(res.json())

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "widgets.widget1.test_text")
    assert workspace_object_exists("Context", "widgets.widget1.components.test_text")
