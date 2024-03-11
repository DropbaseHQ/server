import copy
from unittest.mock import patch

import pytest

base_table_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [
            {
                "label": "Table2",
                "name": "table2",
                "description": None,
                "fetcher": "function3",
                "height": "",
                "size": 10,
                "filters": None,
                "type": "sql",
                "smart": False,
                "columns": [
                    {
                        "name": "customer_id",
                        "column_type": "postgres",
                        "data_type": "int64",
                        "display_type": "integer",
                    },
                    {
                        "name": "company_name",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "contact_name",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "phone_number",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "customer_type",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                ],
            }
        ],
        "widgets": [],
        "files": [
            {"name": "function1", "type": "sql", "source": "dropbasedev", "depends_on": []},
            {"name": "function2", "type": "sql", "source": "dropbasedev", "depends_on": []},
            {"name": "function3", "type": "sql", "source": "dropbasedev", "depends_on": []},
        ],
    },
}

base_smart_table_data = {
    "table": {
        "label": "Table2",
        "name": "table2",
        "description": None,
        "fetcher": "function3",
        "height": "",
        "size": 10,
        "filters": None,
        "type": "sql",
        "smart": False,
        "columns": [
            {
                "name": "customer_id",
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
                "name": "company_name",
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
                "name": "contact_name",
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
                "name": "phone_number",
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
                "name": "customer_type",
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
        ],
    },
    "state": {"tables": {"table1": {}, "table2": {}}, "widgets": {}},
    "app_name": "dropbase_test_app",
    "page_name": "page1",
}


@pytest.mark.parametrize("mock_db", ["postgres"], indirect=True)
def test_convert_to_smart_table(test_client, mocker, mock_db):
    # Arrange
    table_data = copy.deepcopy(base_table_data)
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}

    t1 = test_client.put("/page", json=table_data, headers=headers)
    print(t1.json())

    mocker.patch("server.controllers.tables.connect", return_value=mock_db)
    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()
    print(res_data)
