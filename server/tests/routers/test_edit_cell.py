from sqlalchemy import text

data = {
    # could be ignored, mocking in mock db
    "file": {
        "source": "local",
        "id": "7699d7d1-d01f-487f-9dd2-474d1080a4a0",
        "date": "2023-12-08T21:52:27.613807",
        "page_id": "8ba52662-41c8-485f-a62f-6b14499144e5",
        "name": "demo_sql",
        "type": "sql",
    },
    "edits": [
        {
            "row": {"user_id": 1, "username": "John Doe", "email": "john.doe@example.com"},
            "column_name": "username",
            "columns": {
                "user_id": {
                    "name": "user_id",
                    "type": "INTEGER",
                    "unique": False,
                    "default": "nextval('\"public\".users_user_id_seq'::regclass)",
                    "visible": True,
                    "editable": False,
                    "Noneable": False,
                    "edit_keys": [],
                    "table_name": "users",
                    "column_name": "user_id",
                    "foreign_key": False,
                    "primary_key": True,
                    "schema_name": "public",
                },
                "username": {
                    "name": "username",
                    "type": "VARCHAR(255)",
                    "unique": False,
                    "default": None,
                    "visible": True,
                    "editable": True,
                    "Noneable": False,
                    "edit_keys": ["user_id"],
                    "table_name": "users",
                    "column_name": "username",
                    "foreign_key": False,
                    "primary_key": False,
                    "schema_name": "public",
                },
                "email": {
                    "name": "email",
                    "type": "VARCHAR(255)",
                    "unique": False,
                    "default": None,
                    "visible": True,
                    "editable": False,
                    "Noneable": False,
                    "edit_keys": ["user_id"],
                    "table_name": "users",
                    "column_name": "email",
                    "foreign_key": False,
                    "primary_key": False,
                    "schema_name": "public",
                },
            },
            "old_value": "John Doe",
            "new_value": "Hello World",
        }
    ],
}


def test_edit_cell(test_client, mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect_to_user_db", return_value=mock_db)

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=data)

    with mock_db.connect() as conn:
        res = conn.execute(text("SELECT username FROM users where user_id = 1")).one()
        assert res[0] == "Hello World"  # Assert


def test_edit_cell_db_execute_fail(test_client, mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect_to_user_db", return_value=mock_db)

    # Act
    data["edits"][0]["row"] = {
        "row": {"user_id": 77, "username": "John Doe", "email": "john.doe@example.com"}
    }
    res = test_client.post("/edit_cell/edit_sql_table/", json=data)

    # Assert
    assert res.status_code != 200
