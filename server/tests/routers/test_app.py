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
    with open("workspace/properties.json", "r") as f:
        workspace_properties = json.loads(f.read())
    apps = workspace_properties.get("apps", {})
    assert app_name in apps.keys()


def test_list_apps(client):
    response = client.get("/app/list/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
