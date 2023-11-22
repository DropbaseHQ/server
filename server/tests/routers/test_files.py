import os
import shutil

from server.tests.mocks.dropbase.file import (
    create_file_response,
    delete_file_response,
    update_file_name_response,
)
from server.tests.verify_file_exists import workspace_file_exists
from server.tests.verify_folder_structure import is_valid_folder_structure
from server.tests.constants import WORKSPACE_PATH


def test_create_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "create_file", side_effect=create_file_response)

    data = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "name": "test_file",
        "type": "python",
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
    }

    # Act
    res = test_client.post("/files", json=data)

    # Assert
    assert res.status_code == 200
    assert is_valid_folder_structure()
    assert workspace_file_exists("scripts/test_file.py")


def test_get_all_files(test_client, dropbase_router_mocker):
    # Arrange
    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    shutil.rmtree(scripts_path)
    os.mkdir(scripts_path)

    files = ["test1.py", "test2.py", "test3.sql", "test4.sql"]
    for i in range(len(files)):
        path = scripts_path.joinpath(files[i]).absolute()
        with open(path, "w") as wf:
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
    with open(scripts_path.joinpath("test_rename.sql"), "w") as wf:
        pass

    assert workspace_file_exists("scripts/test_rename.sql")

    data = {
        "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
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


def test_delete_file_req(test_client, dropbase_router_mocker):
    # Arrange
    dropbase_router_mocker.patch("file", "delete_file", side_effect=delete_file_response)

    scripts_path = WORKSPACE_PATH.joinpath("dropbase_test_app/page1/scripts/")
    with open(scripts_path.joinpath("test_delete.sql"), "w") as wf:
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
