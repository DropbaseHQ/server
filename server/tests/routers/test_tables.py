import pandas as pd

from server.tests.constants import WORKSPACE_PATH
from server.tests.mocks.dropbase.sync import sync_columns_response
from server.tests.mocks.dropbase.table import (
    create_table_response,
    delete_table_response,
    update_table_response,
)
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.verify_object_exists import workspace_object_exists


def test_create_table_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("table", "create_table", side_effect=create_table_response)

    data = {
        "name": "test_table",
        "property": {
            "filters": [],
            "appears_after": None,
            "on_row_change": None,
            "on_row_selection": None,
        },
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
    }

    # Act
    res = test_client.post("/tables", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_object_exists("State", "tables.test_table")
    assert workspace_object_exists("Context", "tables.test_table")


def test_update_table_req_file_changed(test_client, dropbase_router_mocker, mocker):
    # Arrange
    test_create_table_req(test_client, dropbase_router_mocker)
    assert workspace_object_exists("State", "tables.test_table")
    assert workspace_object_exists("Context", "tables.test_table")

    dropbase_router_mocker.patch("table", "update_table", side_effect=update_table_response)
    dropbase_router_mocker.patch("sync", "sync_columns", side_effect=sync_columns_response)
    mocker.patch(
        "server.controllers.query.query_db",
        side_effect=lambda *args: pd.DataFrame([[1]], columns=["?column?"]),
    )

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    files = ["test3.sql", "test4.sql"]
    for i in range(len(files)):
        path = scripts_path.joinpath(files[i]).absolute()
        with open(path, "w") as wf:
            wf.write("select 1;")

    data = {
        "name": "test_table_renamed",
        "property": {
            "filters": [],
            "appears_after": None,
            "on_row_change": None,
            "on_row_selection": None,
        },
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "table": {
            "id": "1234",
            "file_id": "1234",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "name": "test_table",
            "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        },
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}, "test_table": {}}},
        "file": {"id": "1235", "name": "test4", "type": "sql"},
    }

    # Act
    res = test_client.put("/tables/7f1dabeb-907b-4e59-8417-ba67a801ba0e", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "tables.test_table")
    assert not workspace_object_exists("Context", "tables.test_table")
    assert workspace_object_exists("State", "tables.test_table_renamed")
    assert workspace_object_exists("Context", "tables.test_table_renamed")


def test_update_table_req_file_unchanged(test_client, dropbase_router_mocker):
    # FIXME handle_state_context_updates is not called when file is unchanged
    return
    # Arrange
    test_create_table_req(test_client, dropbase_router_mocker)
    assert workspace_object_exists("State", "tables.test_table")
    assert workspace_object_exists("Context", "tables.test_table")

    dropbase_router_mocker.patch("table", "update_table", side_effect=update_table_response)

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    files = ["test3.sql", "test4.sql"]
    for i in range(len(files)):
        path = scripts_path.joinpath(files[i]).absolute()
        with open(path, "w") as wf:
            wf.write("select 1;")

    data = {
        "name": "test_table_renamed",
        "property": {
            "filters": [],
            "appears_after": None,
            "on_row_change": None,
            "on_row_selection": None,
        },
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "table": {
            "id": "1234",
            "file_id": "1234",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "name": "test_table",
            "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        },
        "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}, "test_table": {}}},
        "file": {"id": "1234", "name": "test3", "type": "sql"},
    }

    # Act
    res = test_client.put("/tables/7f1dabeb-907b-4e59-8417-ba67a801ba0e", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "tables.test_table")
    assert not workspace_object_exists("Context", "tables.test_table")
    assert workspace_object_exists("State", "tables.test_table_renamed")
    assert workspace_object_exists("Context", "tables.test_table_renamed")


def test_delete_table_req(test_client, dropbase_router_mocker):
    # Arrange
    test_create_table_req(test_client, dropbase_router_mocker)
    assert workspace_object_exists("State", "tables.test_table")
    assert workspace_object_exists("Context", "tables.test_table")

    dropbase_router_mocker.patch("table", "delete_table", side_effect=delete_table_response)

    # Act
    res = test_client.delete("/tables/3f1dabeb-907b-4e59-8417-ba67a801ba0e")

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_object_exists("State", "tables.test_table")
    assert not workspace_object_exists("Context", "tables.test_table")


def test_convert_sql_table_req(test_client):
    # FIXME
    return
    raise NotImplementedError
