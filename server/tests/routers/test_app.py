import os
import shutil

from server.tests.constants import TEST_APP_NAME, WORKSPACE_PATH

NEW_APP_NAME = "test_create_app"
OLD_APP_NAME = "test_create_app_2"


def check_directory_structure(path):
    # Define the paths to check
    paths_to_check = [
        os.path.join(path, "state.py"),
        os.path.join(path, "context.py"),
        os.path.join(path, "properties.json"),
        os.path.join(path, "scripts"),
    ]

    # Check if each path exists
    for path in paths_to_check:
        if not os.path.exists(path):
            return False

    return True


def test_create_app_req(test_client):
    try:
        # Arrange
        data = {"app_name": NEW_APP_NAME}

        # Act
        res = test_client.post("/app/", json=data)

        # Assert
        assert res.status_code == 200
        assert check_directory_structure(f"workspace/{NEW_APP_NAME}/page1")
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath(NEW_APP_NAME), ignore_errors=True)


def test_create_app_req_error_duplicate_names(test_client):
    # Arrange
    data = {"app_name": NEW_APP_NAME}

    # Act
    create_first_app = test_client.post("/app/", json=data)

    res = test_client.post("/app/", json=data)
    res_data = res.json()

    # Assert
    assert create_first_app.status_code == 200
    assert res.status_code != 200

    assert res_data["message"] == "An app with this name already exists"


def test_create_app_req_error_illegal_name_space_between(test_client):
    # Arrange
    data = {"app_name": "My New App"}

    # Act
    res = test_client.post("/app/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure(f"workspace/My New App/page1")

    assert (
        res_data["message"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


def test_create_app_req_error_illegal_name_special_characters(test_client):
    # Arrange
    data = {"app_name": "My_New_App!"}

    # Act
    res = test_client.post("/app/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure(f"workspace/My_New_App/page1")

    assert (
        res_data["message"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


def test_create_app_req_error_illegal_name_url_path(test_client):
    # Arrange
    data = {"app_name": "../../my_app"}

    # Act
    res = test_client.post("/app/", json=data)
    res_data = res.json()

    # Assert
    assert res.status_code != 200

    assert not check_directory_structure(f"workspace/../../my_app/page1")

    assert (
        res_data["message"]
        == "Invalid app name. Only alphanumeric characters and underscores are allowed"
    )


def test_rename_app_req_error_duplicate_names(test_client):
    # Arrange
    data = {"app_name": NEW_APP_NAME}
    create_app = test_client.post("/app/", json=data)

    # Act
    req = {"old_name": OLD_APP_NAME, "new_name": NEW_APP_NAME}

    res = test_client.put("/app/", json=req)
    res_data = res.json()

    # Assert
    assert create_app.status_code == 200
    assert res.status_code != 200

    assert res_data["message"] == "An app with this name already exists"


def test_rename_app_req(test_client):
    try:
        # Arrange
        data = {"old_name": TEST_APP_NAME, "new_name": NEW_APP_NAME}

        # Act
        res = test_client.put("/app/", json=data)

        # Assert
        assert res.status_code == 200
        assert not check_directory_structure(f"workspace/{TEST_APP_NAME}/page1")
        assert check_directory_structure(f"workspace/{NEW_APP_NAME}/page1")
    finally:
        shutil.rmtree(WORKSPACE_PATH.joinpath(NEW_APP_NAME), ignore_errors=True)


def test_delete_app_req(test_client):
    # Act
    res = test_client.request("DELETE", f"/app/{TEST_APP_NAME}")

    # Assert
    assert res.status_code == 200
    assert not check_directory_structure(f"workspace/{TEST_APP_NAME}/page1")


def test_delete_app_req_block_path_traversal_attack(test_client):
    # Arrange
    try:
        test_target_path = WORKSPACE_PATH.parent.joinpath(
            "test_delete_app_req_block_path_traversal_attack_folder"
        )
        test_target_rel_path = (
            "../test_delete_app_req_block_path_traversal_attack_folder"
        )
        os.mkdir(test_target_path)

        # Act
        res = test_client.request("DELETE", f"/app/{test_target_rel_path}")

        # Assert
        assert res.status_code != 200
        assert os.path.exists(test_target_path)
    finally:
        shutil.rmtree(test_target_path)
