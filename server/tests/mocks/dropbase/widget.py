from uuid import UUID

from server.tests.mocks.util import mock_response


def create_widget_response(payload: dict):
    name = payload["property"]["name"]
    name_caps = name.capitalize()
    return mock_response(
        json={
            "app_name": "dropbase_test_app",
            "page_name": "page1",
            "state": {
                "title": "State",
                "type": "object",
                "properties": {
                    "widgets": {"$ref": "#/definitions/WidgetsState"},
                    "tables": {"$ref": "#/definitions/TablesState"},
                },
                "required": ["widgets", "tables"],
                "definitions": {
                    f"{name_caps}State": {
                        "title": f"{name_caps}State",
                        "type": "object",
                        "properties": {},
                    },
                    "WidgetsState": {
                        "title": "WidgetsState",
                        "type": "object",
                        "properties": {name: {"$ref": f"#/definitions/{name_caps}State"}},
                        "required": [name],
                    },
                    "Table1State": {"title": "Table1State", "type": "object", "properties": {}},
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {"table1": {"$ref": "#/definitions/Table1State"}},
                        "required": ["table1"],
                    },
                },
            },
            "context": {
                "title": "Context",
                "type": "object",
                "properties": {
                    "widgets": {"$ref": "#/definitions/WidgetsContext"},
                    "tables": {"$ref": "#/definitions/TablesContext"},
                },
                "required": ["widgets", "tables"],
                "definitions": {
                    f"{name_caps}ComponentsContext": {
                        "title": f"{name_caps}ComponentsContext",
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                    f"{name_caps}Context": {
                        "title": f"{name_caps}Context",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "components": {"$ref": f"#/definitions/{name_caps}ComponentsContext"},
                        },
                        "required": ["components"],
                    },
                    "WidgetsContext": {
                        "title": "WidgetsContext",
                        "type": "object",
                        "properties": {name: {"$ref": f"#/definitions/{name_caps}Context"}},
                        "required": [name],
                    },
                    "PgColumnContextProperty": {
                        "title": "PgColumnContextProperty",
                        "type": "object",
                        "properties": {
                            "editable": {"title": "Editable", "default": False, "type": "boolean"},
                            "visible": {"title": "Visible", "default": True, "type": "boolean"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "Table1ColumnsContext": {
                        "title": "Table1ColumnsContext",
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                    "Table1Context": {
                        "title": "Table1Context",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "columns": {"$ref": "#/definitions/Table1ColumnsContext"},
                        },
                        "required": ["columns"],
                    },
                    "TablesContext": {
                        "title": "TablesContext",
                        "type": "object",
                        "properties": {"table1": {"$ref": "#/definitions/Table1Context"}},
                        "required": ["table1"],
                    },
                },
            },
        }
    )


def update_widget_response(widget_id: UUID, update_data: dict):
    return create_widget_response(update_data)


def delete_widget_response(widget_id: str):
    return mock_response(
        json={
            "app_name": "dropbase_test_app",
            "page_name": "page1",
            "state": {
                "title": "State",
                "type": "object",
                "properties": {
                    "widgets": {"$ref": "#/definitions/WidgetsState"},
                    "tables": {"$ref": "#/definitions/TablesState"},
                },
                "required": ["widgets", "tables"],
                "definitions": {
                    "WidgetsState": {"title": "WidgetsState", "type": "object", "properties": {}},
                    "Table1State": {
                        "title": "Table1State",
                        "type": "object",
                        "properties": {
                            "workspace_id": {"title": "Workspace Id", "type": "string"},
                            "workspace_name": {"title": "Workspace Name", "type": "string"},
                            "is_active": {"title": "Is Active", "type": "string"},
                            "created_at": {"title": "Created At", "type": "string"},
                        },
                    },
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {"table1": {"$ref": "#/definitions/Table1State"}},
                        "required": ["table1"],
                    },
                },
            },
            "context": {
                "title": "Context",
                "type": "object",
                "properties": {
                    "widgets": {"$ref": "#/definitions/WidgetsContext"},
                    "tables": {"$ref": "#/definitions/TablesContext"},
                },
                "required": ["widgets", "tables"],
                "definitions": {
                    "WidgetsContext": {"title": "WidgetsContext", "type": "object", "properties": {}},
                    "PgColumnContextProperty": {
                        "title": "PgColumnContextProperty",
                        "type": "object",
                        "properties": {
                            "editable": {"title": "Editable", "default": False, "type": "boolean"},
                            "visible": {"title": "Visible", "default": True, "type": "boolean"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "Table1ColumnsContext": {
                        "title": "Table1ColumnsContext",
                        "type": "object",
                        "properties": {
                            "workspace_id": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "workspace_name": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "is_active": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "created_at": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["workspace_id", "workspace_name", "is_active", "created_at"],
                    },
                    "Table1Context": {
                        "title": "Table1Context",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "columns": {"$ref": "#/definitions/Table1ColumnsContext"},
                        },
                        "required": ["columns"],
                    },
                    "TablesContext": {
                        "title": "TablesContext",
                        "type": "object",
                        "properties": {"table1": {"$ref": "#/definitions/Table1Context"}},
                        "required": ["table1"],
                    },
                },
            },
        }
    )
