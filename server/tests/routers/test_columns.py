import copy

import pytest

base_data = {
    "app_name": "test9",
    "page_name": "page1",
    "properties": {
        "tables": [
            {
                "label": "Table2",
                "name": "table2",
                "description": None,
                "fetcher": "function1",
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
                        "display_type": "integer",
                        "configurations": {
                            "integer": {"config_type": "int"},
                            "currency": None,
                            "weight": None,
                        },
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

    # column_property_values = request.param

    # data changes here
    return data


@pytest.mark.parametrize("mock_db", ["postgres", "snowflake"], indirect=True)
@pytest.mark.parametrize(
    "get_column_properties_cell_data",
    [
        {
            "column_name": "int_col",
            "configurations": {"currency": {"config_type": "currency", "symbol": "$$"}},
        },
        {
            "column_name": "int_col",
            "configurations": {
                "integer": {
                    "config_type": "int",
                }
            },
        },
        {
            "column_name": "float_col",
            "configurations": {"currency": {"config_type": "currency", "symbol": "$$"}},
        },
        {
            "column_name": "float_col",
            "configurations": {
                "integer": {
                    "config_type": "float",
                }
            },
        },
        {
            "column_name": "string_col",
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
            "column_name": "string_col",
            "configurations": {
                "integer": {
                    "config_type": "text",
                }
            },
        },
    ],
    indirect=True,
)
def test_column_properties(test_client, mocker, mock_db, get_edit_cell_data):
    # Arrange
    mocker.patch("server.controllers.edit_cell.connect", return_value=mock_db)

    # cell_data = get_edit_cell_data

    # Act
    # Assert
