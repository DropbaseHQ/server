import copy

import pytest

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "blocks": [
            {
                "block_type": "table",
                "label": "Table1",
                "name": "table1",
                "description": None,
                "fetcher": "function1",
                "widget": None,
                "size": 10,
                "filters": None,
                "w": 4,
                "h": 1,
                "x": 0,
                "y": 0,
                "type": "sql",
                "smart": False,
                "columns": [
                    {
                        "name": "id",
                        "data_type": "int64",
                        "display_type": "currency",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "date",
                        "data_type": "object",
                        "display_type": "date",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "time",
                        "data_type": "object",
                        "display_type": "time",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "string",
                        "data_type": "object",
                        "display_type": "text",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "int",
                        "data_type": "int64",
                        "display_type": "integer",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "float",
                        "data_type": "float64",
                        "display_type": "float",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "bool",
                        "data_type": "bool",
                        "display_type": "boolean",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                    {
                        "name": "timestamp",
                        "data_type": "datetime64[ns]",
                        "display_type": "datetime",
                        "configurations": None,
                        "schema_name": None,
                        "table_name": None,
                        "column_name": None,
                        "primary_key": False,
                        "foreign_key": False,
                        "default": None,
                        "Noneable": False,
                        "unique": False,
                        "edit_keys": [],
                        "column_type": "postgres",
                        "hidden": False,
                        "editable": False,
                    },
                ],
            }
        ],
        "widgets": [],
        "files": [
            {"name": "function1", "type": "sql", "source": "dropbasedev", "depends_on": []},
            {"name": "function2", "type": "sql", "source": "mydb2", "depends_on": []},
        ],
    },
}


@pytest.fixture(scope="session")
def get_column_properties_data(request, test_client):
    # Arrange
    data = copy.deepcopy(base_data)

    for column in data["properties"]["blocks"][0]["columns"]:
        if column["name"] == request.param["column_name"]:
            column["configurations"] = request.param["configurations"]

    return data


@pytest.mark.parametrize("mock_db", ["postgres", "snowflake", "mysql", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "get_column_properties_data",
    [
        {
            "column_name": "int",
            "configurations": {"currency": {"config_type": "currency", "symbol": "$$"}},
        },
        {
            "column_name": "int",
            "configurations": {
                "integer": {
                    "config_type": "integer",
                }
            },
        },
        {
            "column_name": "float",
            "configurations": {"currency": {"config_type": "currency", "symbol": "$$"}},
        },
        {
            "column_name": "float",
            "configurations": {
                "float": {
                    "config_type": "float",
                }
            },
        },
        {
            "column_name": "string",
            "configurations": {
                "select": {
                    "options": [
                        {
                            "id": "a6d206e7-02d9-48f4-b538-b7dac370d972",
                            "name": "name1",
                            "value": "value1",
                        },
                        {
                            "id": "bee35b94-180a-4ec6-8af6-98afaec6b906",
                            "name": "name2",
                            "value": "value2",
                        },
                    ]
                }
            },
        },
        {
            "column_name": "string",
            "configurations": {
                "text": {
                    "config_type": "text",
                }
            },
        },
    ],
    indirect=True,
)
def test_column_properties(test_client, mocker, mock_db, get_column_properties_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    properties_data = get_column_properties_data
    headers = {"access-token": "mock access token"}

    # Act
    res = test_client.put("/page", json=properties_data, headers=headers)
    res_data = res.json()

    # Assert
    assert res.status_code == 200
    assert res_data["message"] == "Properties updated successfully"
