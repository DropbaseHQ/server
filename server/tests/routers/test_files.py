import os
import shutil

from server.tests.constants import PAGE_ID, WORKSPACE_PATH
from server.tests.mocks.dropbase.file import (
    create_file_response,
    delete_file_response,
    update_file_name_response,
    update_file_response,
)
from server.tests.mocks.util import mock_response
from server.tests.verify_file_exists import workspace_file_exists
from server.tests.verify_folder_structure import is_valid_folder_structure


def test_create_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "create_file", side_effect=create_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "test_file",
        "type": "sql",
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_file.sql")


def test_create_file_req_ui(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "create_file", side_effect=create_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "test_file",
        "type": "ui",
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_file.py")


def test_create_file_req_data_fetcher(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "create_file", side_effect=create_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "test_file",
        "type": "data_fetcher",
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_file.py")


def test_create_file_req_bad_request(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch(
        "file",
        "create_file",
        side_effect=lambda *args, **kwargs: mock_response(json={}, status_code=500),
    )

    data = {
        "app_name": "dropbase_test_appadasdadsd",
        "page_name": "page1",
        "name": "test_file",
        "type": "random gibberish type",
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code != 200
    assert is_valid_folder_structure()
    assert not workspace_file_exists("scripts/test_file.py")


def test_create_file_req_block_path_traversal_vulnerability(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "create_file", side_effect=create_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "../test_file",
        "type": "random gibberish type",
        "page_id": PAGE_ID,
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code != 200
    assert is_valid_folder_structure()
    assert not workspace_file_exists("test_file.py")


def test_get_all_files(test_client):
    # Arrange
    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    shutil.rmtree(scripts_path)
    os.mkdir(scripts_path)

    files = ["test1.py", "test2.py", "test3.sql", "test4.sql", "test5.sql"]
    for i in range(len(files)):
        path = scripts_path.joinpath(files[i]).absolute()
        with open(path, "w") as _:
            pass
        files[i] = str(path)

    # Act
    res = test_client.get("/files/all/dropbase_test_app/page1")

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert set(res.json()["files"]) == set(files)


def test_rename_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "update_file_name", side_effect=update_file_name_response)

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    with open(scripts_path.joinpath("test_rename.sql"), "w") as _:
        pass

    assert workspace_file_exists("scripts/test_rename.sql")

    data = {
        "page_id": PAGE_ID,
        "old_name": "test_rename",
        "new_name": "test_renamed",
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "type": "sql",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_file_exists("scripts/test_rename.sql")
    assert workspace_file_exists("scripts/test_renamed.sql")


def test_rename_file_req_dropbase_call_failed(test_client, dropbase_router_mocker):
    # Arrange
    update_file_name_response_failure = lambda *args, **kwargs: mock_response(  # noqa
        json={"message": "No record present"}, status_code=400, text="fail"
    )
    dropbase_router_mocker.patch(
        "file", "update_file_name", side_effect=update_file_name_response_failure
    )

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    with open(scripts_path.joinpath("test_rename.sql"), "w") as _:
        pass

    assert workspace_file_exists("scripts/test_rename.sql")

    data = {
        "page_id": PAGE_ID,
        "old_name": "test_rename",
        "new_name": "test_renamed",
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "type": "sql",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 400
    assert res.json()["status"] == "error"
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_rename.sql")
    assert not workspace_file_exists("scripts/test_renamed.sql")


def test_rename_file_req_file_not_exists(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "update_file_name", side_effect=update_file_name_response)

    assert not workspace_file_exists("scripts/test_rename.sql")

    data = {
        "page_id": PAGE_ID,
        "old_name": "test_rename",
        "new_name": "test_renamed",
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "type": "sql",
    }

    # Act
    res = test_client.put("/files/rename", json=data)

    # Assert
    assert res.status_code == 400
    assert res.json()["status"] == "error"
    assert is_valid_folder_structure()


def test_delete_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "delete_file", side_effect=delete_file_response)

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    with open(scripts_path.joinpath("test_delete.sql"), "w") as _:
        pass

    assert workspace_file_exists("scripts/test_delete.sql")

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_name": "test_delete.sql",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/8f1dabeb-907b-4e59-8417-ba67a801ba0e/", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert not workspace_file_exists("scripts/test_delete.sql")


def test_delete_file_req_platform_error(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch(
        "file",
        "delete_file",
        side_effect=lambda *args, **kwargs: mock_response(json={}, status_code=500),
    )

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    with open(scripts_path.joinpath("test_delete.sql"), "w") as _:
        pass

    assert workspace_file_exists("scripts/test_delete.sql")

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_name": "test_delete.sql",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/8f1dabeb-907b-4e59-8417-ba67a801ba0e/", json=data)

    # Assert
    assert res.status_code != 200
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_delete.sql")


def test_delete_file_req_not_exists(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "delete_file", side_effect=delete_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "file_name": "test_delete.sql",
        "type": "sql",
    }

    # Act
    res = test_client.request("DELETE", "/files/8f1dabeb-907b-4e59-8417-ba67a801ba0e/", json=data)

    # Assert
    assert res.status_code != 200


def test_update_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "update_file", side_effect=update_file_response)
    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "test_sql",
        "sql": "mock sql",
        "file_id": PAGE_ID,
        "type": "sql",
    }

    # Act
    res = test_client.put("/files/8f1dabeb-907b-4e59-8417-ba67a801ba0e", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()

    with open(WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/test_sql.sql"), "r") as rf:
        assert rf.read() == "mock sql"
