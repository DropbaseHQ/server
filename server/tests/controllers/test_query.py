import copy

import pytest

from dropbase.schemas.table import TableFilter, TableSort

base_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "table": {
        "label": "Table1",
        "name": "table1",
        "description": None,
        "fetcher": "",
        "height": "",
        "size": 10,
        "filters": None,
        "type": "sql",
        "smart": True,
        "columns": [
            {
                "name": "user_id",
                "data_type": "INTEGER",
                "display_type": "integer",
                "configurations": None,
                "column_type": "postgres",
                "table_name": "users",
                "column_name": "user_id",
                "primary_key": True,
                "foreign_key": False,
                "default": None,
                "nullable": True,
                "unique": False,
                "edit_keys": [],
                "hidden": False,
                "editable": False,
            },
            {
                "name": "username",
                "data_type": "VARCHAR(255)",
                "display_type": "text",
                "configurations": None,
                "column_type": "postgres",
                "table_name": "users",
                "column_name": "username",
                "primary_key": False,
                "foreign_key": False,
                "default": None,
                "nullable": False,
                "unique": False,
                "edit_keys": ["user_id"],
                "hidden": False,
                "editable": False,
            },
            {
                "name": "email",
                "data_type": "VARCHAR(255)",
                "display_type": "text",
                "configurations": None,
                "column_type": "postgres",
                "table_name": "users",
                "column_name": "email",
                "primary_key": False,
                "foreign_key": False,
                "default": None,
                "nullable": False,
                "unique": False,
                "edit_keys": ["user_id"],
                "hidden": False,
                "editable": False,
            },
        ],
    },
    "state": {"tables": {"table1": {}}, "widgets": {}},
    "context": {
        "tables": {
            "table1": {
                "message": None,
                "message_type": None,
                "reload": False,
                "columns": {
                    "user_id": {"visible": None, "message": None, "message_type": None},
                    "username": {"visible": None, "message": None, "message_type": None},
                    "email": {"visible": None, "message": None, "message_type": None},
                },
            }
        },
        "widgets": {},
    },
    "filter_sort": {"filters": [], "sorts": [], "pagination": {"page": 0, "page_size": 10}},
}


@pytest.mark.parametrize(
    "mock_db", ["postgres", "mysql", "snowflake", "sqlite", "sqlite"], indirect=True
)
def test_query_db(mocker, mock_db):
    # Arrange
    mocker.patch("dropbase.database.connect.connect_to_user_db", return_value=mock_db)

    # Act
    output = mock_db._run_query("select * from users;", {})

    # Assert
    # TODO: improve assertions
    assert len(output) > 0
    assert len(output[0]) > 0


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_apply_filters(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["filter_sort"]["filters"] = [
        {
            "column_name": "user_id",
            "value": 1,
            "condition": "=",
            "id": "ee446ffd-6427-4118-be46-4f2971c94b7d",
            "column_type": "integer",
        }
    ]
    data["table"]["fetcher"] = "test_sql"

    mocker.patch("server.controllers.run_sql.connect_to_user_db", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["type"] == "table"
    assert isinstance(res_data["data"], list)
    assert isinstance(res_data["columns"], list)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
def test_apply_sorts(test_client, mocker, mock_db):
    # Arrange
    data = copy.deepcopy(base_data)
    data["filter_sort"]["sorts"] = [{"column_name": "user_id", "value": "desc"}]
    data["table"]["fetcher"] = "test_sql"

    mocker.patch("server.controllers.run_sql.connect_to_user_db", return_value=mock_db)

    # Act
    res = test_client.post("/query", json=data)
    response_data = res.json()
    job_id = response_data["job_id"]

    import time

    time.sleep(2)

    res = test_client.get(f"/query/status/{job_id}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["type"] == "table"
    assert isinstance(res_data["data"], list)
    assert isinstance(res_data["columns"], list)
