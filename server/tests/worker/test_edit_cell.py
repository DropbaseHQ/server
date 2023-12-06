import unittest.mock


def test_edit_cell(test_client, mocker):
    # Arrange
    mock_db = unittest.mock.MagicMock()
    mocker.patch("server.controllers.edit_cell.connect_to_user_db", return_value=mock_db)
    from server.controllers.edit_cell import edit_cell

    # Act
    _ = edit_cell(
        file={"source": "mock_db"},
        edits=[
            {
                "column_name": "name",
                "old_value": "trevor",
                "new_value": "rovert",
                "row": {"id": "trevors_id"},
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
                    },
                },
            }
        ],
    )

    # Assert
    sql_text, values = mock_db.connect().__enter__().execute.call_args.args
    assert 'UPDATE "public"."users"' in str(sql_text)
    assert "SET name = :new_value" in str(sql_text)
    assert "WHERE id = :id AND name = :old_value" in str(sql_text)
    assert values == {"new_value": "rovert", "old_value": "trevor", "id": "trevors_id"}


def test_edit_cell_db_execute_fail(test_client, mocker):
    # Arrange
    mock_db = unittest.mock.MagicMock()
    mock_db.connect().__enter__().execute.side_effect = Exception()
    mocker.patch("server.controllers.edit_cell.connect_to_user_db", return_value=mock_db)
    from server.controllers.edit_cell import edit_cell

    # Act
    output = edit_cell(
        file={"source": "mock_db"},
        edits=[
            {
                "column_name": "name",
                "old_value": "trevor",
                "new_value": "rovert",
                "row": {"id": "trevors_id"},
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
                    },
                },
            }
        ],
    )

    # Assert
    assert "failed to update" in output["result"][0]
