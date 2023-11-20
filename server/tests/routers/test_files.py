from server.tests.mocks.dropbase.file import create_file_response
from server.tests.verify_file_exists import workspace_file_exists
from server.tests.verify_folder_structure import is_valid_folder_structure


def test_create_file_req(test_client, mocker):
    # Arrange
    mocker.patch("server.requests.create_file", side_effect=create_file_response)

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
