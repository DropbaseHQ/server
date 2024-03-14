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


def to_epoch_ms(date_str, is_timestamp):
    fmt = "%Y-%m-%d %H:%M:%S" if is_timestamp else "%Y-%m-%d"
    dt = datetime.strptime(date_str, fmt)

    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def convert_epoch_to_datetime(epoch_str):
    epoch_s = epoch_str / 1000.0
    dt = datetime.fromtimestamp(epoch_s, tz=timezone.utc)
    new_value_formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
    tz_formatted = dt.strftime("%z")
    # Insert a colon between the hours and minutes of the timezone
    tz_with_colon = tz_formatted[:-2] + ":" + tz_formatted[-2:]
    return new_value_formatted + tz_with_colon


@pytest.fixture(scope="session")
def get_edit_cell_data(request, test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    edit_values = request.param

    data["edits"][0]["column_name"] = edit_values["column_name"]
    data["edits"][0]["data_type"] = edit_values["data_type"]

    if "TIMESTAMP" in edit_values["data_type"]:
        data["edits"][0]["old_value"] = to_epoch_ms(edit_values["old_value"], is_timestamp=True)
        data["edits"][0]["new_value"] = to_epoch_ms(edit_values["new_value"], is_timestamp=True)
    elif "DATE" in edit_values["data_type"]:
        data["edits"][0]["old_value"] = to_epoch_ms(edit_values["old_value"], is_timestamp=False)
        data["edits"][0]["new_value"] = to_epoch_ms(edit_values["new_value"], is_timestamp=False)
    else:
        data["edits"][0]["old_value"] = edit_values["old_value"]
        data["edits"][0]["new_value"] = edit_values["new_value"]

    return data


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "get_edit_cell_data",
    [
        {
            "column_name": "datetime_col",
            "data_type": "TIMESTAMP WITHOUT TIME ZONE",
            "old_value": "2024-03-14 15:00:00",
            "new_value": "2024-03-20 16:00:00",
        },
        {
            "column_name": "date_col",
            "data_type": "DATE",
            "old_value": "2024-03-14",
            "new_value": "2024-06-20",
        },
        {
            "column_name": "time_col",
            "data_type": "TIME WITHOUT TIME ZONE",
            "old_value": "15:00:00",
            "new_value": "21:00:00",
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
def test_edit_cell(test_client, mocker, mock_db, get_edit_cell_data):
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
        new_value = convert_epoch_to_datetime(new_value)

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
