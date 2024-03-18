import copy
from datetime import datetime, timezone

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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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
                    "table_name": "alltypes",
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


def convert_timestamp_to_datetime(timestamp):
    timestamp_seconds = timestamp / 1000
    date_time_obj = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
    date_time = date_time_obj.strftime("%Y-%m-%d %H:%M:%S%z")
    date_time = date_time[:-2] + ":" + date_time[-2:]
    return date_time


@pytest.fixture(scope="session")
def get_edit_cell_data(request, test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    edit_values = request.param

    data["edits"][0]["column_name"] = edit_values["column_name"]
    data["edits"][0]["data_type"] = edit_values["data_type"]

    data["edits"][0]["old_value"] = edit_values["old_value"]
    data["edits"][0]["new_value"] = edit_values["new_value"]

    return data


@pytest.mark.parametrize("mock_db", ["postgres", "snowflake"], indirect=True)
@pytest.mark.parametrize(
    "get_edit_cell_data",
    [
        {
            "column_name": "datetime_col",
            "data_type": "TIMESTAMP WITHOUT TIME ZONE",
            "old_value": 1711738800000,
            "new_value": 1711206000000,
        },
        {
            "column_name": "date_col",
            "data_type": "DATE",
            "old_value": 1707955200000,
            "new_value": 1707868800000,
        },
        {
            "column_name": "time_col",
            "data_type": "TIME WITHOUT TIME ZONE",
            "old_value": "10:03:00",
            "new_value": "15:00:00",
        },
        {
            "column_name": "string_col",
            "data_type": "VARCHAR(255)",
            "old_value": "First Entry",
            "new_value": "Hello World",
        },
        {
            "column_name": "int_col",
            "data_type": "INTEGER",
            "old_value": 1,
            "new_value": 10,
        },
        {
            "column_name": "float_col",
            "data_type": "REAL",
            "old_value": 1.1,
            "new_value": 10.1,
        },
        {
            "column_name": "bool_col",
            "data_type": "BOOLEAN",
            "old_value": True,
            "new_value": False,
        },
    ],
    indirect=True,
)
def test_edit_postgres_snowflake_cell(test_client, mocker, mock_db, get_edit_cell_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    cell_data = get_edit_cell_data

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=cell_data)
    res_data = res.json()

    column_name = cell_data["edits"][0]["column_name"]
    new_value = cell_data["edits"][0]["new_value"]
    old_value = cell_data["edits"][0]["old_value"]

    if "datetime_col" in column_name or "date_col" in column_name:
        new_value = convert_timestamp_to_datetime(new_value)

    assert res.status_code == 200
    assert res_data["result"] == [f"Updated {column_name} from {old_value} to {new_value}"]


@pytest.mark.parametrize("mock_db", ["mysql", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "get_edit_cell_data",
    [
        {
            "column_name": "datetime_col",
            "data_type": "TIMESTAMP WITHOUT TIME ZONE",
            "old_value": 1711738800000,
            "new_value": 1711206000000,
        },
        {
            "column_name": "date_col",
            "data_type": "DATE",
            "old_value": 1707955200000,
            "new_value": 1707868800000,
        },
        {
            "column_name": "time_col",
            "data_type": "TIME WITHOUT TIME ZONE",
            "old_value": "10:03:00",
            "new_value": "15:00:00",
        },
        {
            "column_name": "string_col",
            "data_type": "VARCHAR(255)",
            "old_value": "First Entry",
            "new_value": "Hello World",
        },
        {
            "column_name": "int_col",
            "data_type": "INTEGER",
            "old_value": 1,
            "new_value": 10,
        },
        {
            "column_name": "float_col",
            "data_type": "REAL",
            "old_value": 1.1,
            "new_value": 10.1,
        },
        {
            "column_name": "bool_col",
            "data_type": "BOOLEAN",
            "old_value": True,
            "new_value": False,
        },
    ],
    indirect=True,
)
def test_edit_mysql_sqlite_cell(test_client, mocker, mock_db, get_edit_cell_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    cell_data = get_edit_cell_data

    # Act
    res = test_client.post("/edit_cell/edit_sql_table/", json=cell_data)
    res_data = res.json()

    column_name = cell_data["edits"][0]["column_name"]
    new_value = cell_data["edits"][0]["new_value"]
    old_value = cell_data["edits"][0]["old_value"]

    assert res.status_code == 200
    assert res_data["result"] == [f"Updated {column_name} from {old_value} to {new_value}"]


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_edit_cell_db_execute_fail(test_client, mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)
    data = copy.deepcopy(base_data)
    # Act
    data["edits"][0]["row"] = {
        "user_id": 100,
        "datetime_col": "2024-03-14 15:00:00",
        "date_col": "2024-03-14",
        "time_col": "15:00:00",
        "string_col": "First Entry",
        "int_col": 1,
        "float_col": 1.1,
        "bool_col": True,
    }

    res = test_client.post("/edit_cell/edit_sql_table/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200
    assert res_data["result"] == [
        "Failed to update string_col from First Entry to Hello World. Error: No rows were updated"
    ]
