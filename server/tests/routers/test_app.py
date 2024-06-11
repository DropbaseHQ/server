import json
import os


def test_create_app(client):
    app_name, app_label = "test_app", "Test App"
    response = client.post("/app/", json={"app_name": app_name, "app_label": app_label})
    assert response.status_code == 200
    assert response.json() == {"message": f"App {app_name} created successfully"}

    # assert app directory is created in workspace folder
    assert os.path.exists(f"workspace/{app_name}")

    # check is app is added to workspace properties.json
    apps = _get_workspace_apps()
    assert app_name in apps.keys()
    assert apps[app_name]["label"] == app_label


def test_delete_app(client):
    app_name = "app_delete"
    response = client.delete(f"/app/{app_name}")
    assert response.status_code == 200
    assert response.json() == {"message": f"App {app_name} deleted successfully"}

    # assert app directory is deleted from workspace folder
    assert not os.path.exists(f"workspace/{app_name}")

    # check is app is removed from workspace properties.json
    apps = _get_workspace_apps()
    assert app_name not in apps.keys()


def test_rename_app(client):
    app_name, new_label = "app_rename", "Renamed App"
    response = client.put("/app/", json={"app_name": app_name, "new_label": new_label})
    assert response.status_code == 200
    assert response.json() == {"message": f"App {app_name} renamed successfully"}

    # NOTE: only changing app label is allowed, app name and directory name is not changed

    # check is app is renamed in workspace properties.json
    apps = _get_workspace_apps()
    assert app_name in apps.keys()
    assert apps[app_name]["label"] == new_label


def test_list_apps(client):
    response = client.get("/app/list/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def _get_workspace_apps():
    with open("workspace/properties.json", "r") as f:
        workspace_properties = json.loads(f.read())
    apps = workspace_properties.get("apps", {})
    return apps
