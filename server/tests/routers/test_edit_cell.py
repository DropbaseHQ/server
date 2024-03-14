import copy
import time

import pytest

base_data = {
    "file": {"name": "demo_sql", "type": "sql", "source": "local", "depends_on": []},
    "edits": [
        {
            "row": {
                "user_id": 1,
                "datetime_col": "2024-03-14 15:00:00",
                "date_col": "2024-03-14",
                "time_col": "15:00:00",
                "string_col": "First Entry",
                "int_col": 1,
                "float_col": 1.1,
                "bool_col": True,
            },
            "column_name": "string_col",
            "data_type": "VARCHAR(255)",
            "old_value": "First Entry",
            "new_value": "Hello World",
            "columns": [
                {
                    "name": "user_id",
                    "data_type": "SERIAL",
                    "display_type": "integer",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "user_id",
                    "primary_key": True,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": False,
                    "unique": True,
                    "edit_keys": [],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": False,
                },
                {
                    "name": "datetime_col",
                    "data_type": "TIMESTAMP WITHOUT TIME ZONE",
                    "display_type": "timestamp",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "datetime_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "date_col",
                    "data_type": "DATE",
                    "display_type": "date",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "date_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "time_col",
                    "data_type": "TIME WITHOUT TIME ZONE",
                    "display_type": "time",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "time_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "string_col",
                    "data_type": "VARCHAR(255)",
                    "display_type": "text",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "string_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "int_col",
                    "data_type": "INTEGER",
                    "display_type": "integer",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "int_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "float_col",
                    "data_type": "REAL",
                    "display_type": "float",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "float_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
                {
                    "name": "bool_col",
                    "data_type": "BOOLEAN",
                    "display_type": "boolean",
                    "schema_name": "public",
                    "table_name": "AllTypes",
                    "column_name": "bool_col",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "Noneable": True,
                    "unique": False,
                    "edit_keys": ["user_id"],
                    "column_type": "postgres",
                    "hidden": False,
                    "editable": True,
                },
            ],
        }
    ],
}


@pytest.fixture(scope="session")
def get_edit_cell_data(request, test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    edit_values = request.param

    data["edits"][0]["row"] = edit_values["row"]
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
            "row": {
                "user_id": 1,
                "datetime_col": "2024-03-14 15:00:00",
                "date_col": "2024-03-14",
                "time_col": "15:00:00",
                "string_col": "First Entry",
                "int_col": 1,
                "float_col": 1.1,
                "bool_col": True,
            },
            "column_name": "string_col",
            "data_type": "VARCHAR(255)",
            "old_value": "First Entry",
            "new_value": "Hello World",
        },
    ],
    indirect=True,
)
def test_edit_cell(test_client, mocker, mock_db, get_edit_cell_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=get_edit_cell_data)
    res_data = res.json()

    assert res.status_code == 200
    assert res_data["result"] == ["Updated username from First Entry to Hello World"]


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

    time.sleep(3)

    print(res_data)

    # Assert
    assert res.status_code != 200
    assert res_data["result"] == [
        "Failed to update string_col from First Entry to Hello World. Error: No rows were updated"
    ]
