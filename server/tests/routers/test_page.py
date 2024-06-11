import json
import os


def test_get_page(client):
    app_name, page_name = "pages", "page1"
    response = client.get(f"/page/{app_name}/{page_name}")
    assert response.status_code == 200
    assert response.json() == get_page1_response


def test_get_page_methods(client):
    app_name, page_name = "pages", "page3"
    response = client.get(f"/page/{app_name}/{page_name}/methods")
    assert response.status_code == 200
    assert response.json() == get_page3_method_response


def test_create_page(client):
    app_name, page_name, page_label = "pages", "test_page", "Test Page"
    payload = {"app_name": app_name, "page_name": page_name, "page_label": page_label}
    response = client.post("/page/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"Page {page_name} created successfully"}

    # assert app directory is created in workspace folder
    assert os.path.exists(f"workspace/{app_name}/{page_name}")

    # check if app is added to workspace properties.json
    pages = _get_app_pages(app_name)
    assert page_name in pages.keys()
    assert pages[page_name]["label"] == page_label


def test_rename_page(client):
    app_name, page_name, page_label = "pages", "page2", "Renamed Page"
    payload = {"app_name": app_name, "page_name": page_name, "page_label": page_label}
    response = client.put("/page/rename/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": f"Page {page_name} renamed successfully"}

    # check if page label is updated in app properties.json
    pages = _get_app_pages(app_name)
    assert page_name in pages.keys()
    assert pages[page_name]["label"] == page_label


def test_delete_page(client):
    app_name, page_name = "pages", "page2"
    response = client.delete(f"/page/{app_name}/{page_name}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Page {page_name} deleted successfully"}

    # check if page directory is deleted in workspace folder
    assert not os.path.exists(f"workspace/{app_name}/{page_name}")

    # check if page is removed from app properties.json
    pages = _get_app_pages(app_name)
    assert page_name not in pages.keys()


def _get_app_pages(app_name):
    with open(f"workspace/{app_name}/properties.json", "r") as f:
        pages = json.loads(f.read())
    # TODO: update this when pages are moved to it's own section in props.json
    # pages = app_properties.get("pages", {})
    return pages


get_page1_response = {
    "state": {"table1": {"columns": {}, "header": {}, "footer": {}}, "widget1": {"components": {}}},
    "context": {
        "page": {"message": None, "message_type": None},
        "table1": {
            "data": {"type": None, "columns": None, "data": None},
            "message": None,
            "message_type": None,
            "reload": False,
            "columns": {},
            "header": {},
            "footer": {},
        },
        "widget1": {"visible": None, "message": None, "message_type": None, "components": {}},
    },
    "properties": {
        "table1": {
            "block_type": "table",
            "label": "Table 1",
            "name": "table1",
            "description": None,
            "columns": [],
            "header": [],
            "footer": [],
            "w": 3,
            "h": 1,
            "x": 0,
            "y": 0,
        },
        "widget1": {
            "block_type": "widget",
            "label": "Widget 1",
            "name": "widget1",
            "description": None,
            "type": "base",
            "in_menu": True,
            "components": [],
            "w": 1,
            "h": 1,
            "x": 3,
            "y": 0,
        },
    },
    "methods": {"table1": {"columns": {}, "header": {}, "footer": {}, "methods": ["get"]}},
}


get_page3_method_response = {
    "table1": {
        "columns": {},
        "header": {"button1": ["on_click"]},
        "footer": {},
        "methods": ["get", "update"],
    },
    "widget1": {"components": {"input1": ["on_submit"], "button1": ["on_click"]}},
}
