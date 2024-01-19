from server.tests.mocks.util import mock_response


def sync_components_response_empty(app_name: str, page_name: str, token: str):
    # no components
    return mock_response(
        json={
            "app_name": app_name,
            "page_name": page_name,
            "state": {
                "title": "State",
                "type": "object",
                "properties": {
                    "widgets": {"$ref": "#/definitions/WidgetsState"},
                    "tables": {"$ref": "#/definitions/TablesState"},
                },
                "required": ["widgets", "tables"],
                "definitions": {
                    "Widget1State": {"title": "Widget1State", "type": "object", "properties": {}},
                    "WidgetsState": {
                        "title": "WidgetsState",
                        "type": "object",
                        "properties": {"widget1": {"$ref": "#/definitions/Widget1State"}},
                        "required": ["widget1"],
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
                    "Widget1ComponentsContext": {
                        "title": "Widget1ComponentsContext",
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                    "Widget1Context": {
                        "title": "Widget1Context",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "components": {"$ref": "#/definitions/Widget1ComponentsContext"},
                        },
                        "required": ["components"],
                    },
                    "WidgetsContext": {
                        "title": "WidgetsContext",
                        "type": "object",
                        "properties": {"widget1": {"$ref": "#/definitions/Widget1Context"}},
                        "required": ["widget1"],
                    },
                    "Table1ColumnsContext": {
                        "title": "Table1ColumnsContext",
                        "type": "object",
                        "properties": {},
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
