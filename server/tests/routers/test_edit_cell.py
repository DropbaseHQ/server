import copy

import pytest

base_data = {
    # could be ignored, mocking in mock db
    "file": {"name": "demo_sql", "type": "sql", "source": "local", "depends_on": []},
    "edits": [
        {
            "row": {"user_id": 1, "username": "John Doe", "email": "john.doe@example.com"},
            "column_name": "username",
            "data_type": "VARCHAR(255)",
            "columns": [
                {
                    "name": "user_id",
                    "data_type": "INTEGER",
                    "display_type": "integer",
                    "unique": False,
                    "default": "nextval('\"public\".users_user_id_seq'::regclass)",
                    "visible": True,
                    "editable": False,
                    "edit_keys": ["user_id"],
                    "table_name": "users",
                    "column_name": "user_id",
                    "foreign_key": False,
                    "primary_key": True,
                    "schema_name": "public",
                    "nullable": False,
                },
                {
                    "name": "username",
                    "data_type": "VARCHAR(255)",
                    "display_type": "text",
                    "unique": False,
                    "default": None,
                    "visible": True,
                    "editable": True,
                    "edit_keys": ["user_id"],
                    "table_name": "users",
                    "column_name": "username",
                    "foreign_key": False,
                    "primary_key": False,
                    "schema_name": "public",
                    "nullable": True,
                },
                {
                    "name": "email",
                    "data_type": "VARCHAR(255)",
                    "display_type": "text",
                    "unique": False,
                    "default": None,
                    "visible": True,
                    "editable": False,
                    "edit_keys": ["user_id"],
                    "table_name": "users",
                    "column_name": "email",
                    "foreign_key": False,
                    "primary_key": False,
                    "schema_name": "public",
                    "nullable": True,
                },
            ],
            "column_type": "INTEGER",
            "old_value": "John Doe",
            "new_value": "Hello World",
        }
    ],
}


@pytest.fixture(scope="session")
def get_edit_cell_data(request, test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    edit_values = request.param

    data["edits"][0]["row"] = edit_values["row"]
    data["edits"][0]["data_type"] = edit_values["data_type"]
    data["edits"][0]["column_name"] = edit_values["column_name"]
    data["edits"][0]["data_type"] = edit_values["data_type"]
    data["edits"][0]["old_value"] = edit_values["old_value"]
    data["edits"][0]["new_value"] = edit_values["new_value"]

    return data


@pytest.mark.parametrize("mock_db", ["postgres"], indirect=True)
@pytest.mark.parametrize(
    "get_edit_cell_data",
    [
        {
            "row": {"user_id": 1, "username": "John Doe", "email": "john.doe@example.com"},
            "column_name": "username",
            "data_type": "VARCHAR(255)",
            "column_type": "INTEGER",
            "old_value": "John Doe",
            "new_value": "Hello World",
        }
    ],
    indirect=True,
)
def test_edit_cell(test_client, mocker, mock_db, get_edit_cell_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=base_data)
    res_data = res.json()

    assert res.status_code == 200
    assert res_data["result"] == ["Updated username from John Doe to Hello World"]


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_edit_cell_db_execute_fail(test_client, mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    # Act
    base_data["edits"][0]["row"] = {
        "user_id": 77,
        "username": "John Doe",
        "email": "john.doe@example.com",
    }
    res = test_client.post("/edit_cell/edit_sql_table/", json=base_data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200
    assert res_data["result"] == [
        "Failed to update username from John Doe to Hello World. Error: No rows were updated"
    ]
