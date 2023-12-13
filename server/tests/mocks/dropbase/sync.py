from server.tests.mocks.util import mock_response


def sync_columns_response(payload: dict):
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
                    "Widget1State": {
                        "title": "Widget1State",
                        "type": "object",
                        "properties": {},
                    },
                    "WidgetsState": {
                        "title": "WidgetsState",
                        "type": "object",
                        "properties": {"widget1": {"$ref": "#/definitions/Widget1State"}},
                        "required": ["widget1"],
                    },
                    "Table1State": {
                        "title": "Table1State",
                        "type": "object",
                        "properties": {},
                    },
                    "Test_table_renamedState": {
                        "title": "Test_table_renamedState",
                        "type": "object",
                        "properties": {
                            "test_column": {"title": "test_column", "default": "str", "type": "string"},
                        },
                    },
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1State"},
                            "test_table_renamed": {"$ref": "#/definitions/Test_table_renamedState"},
                        },
                        "required": ["table1", "test_table_renamed"],
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
                    "Test_table_renamedColumnsContext": {
                        "title": "Test_table_renamedColumnsContext",
                        "type": "object",
                        "properties": {
                            "test_column": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["test_column"],
                    },
                    "Test_table_renamedContext": {
                        "title": "Test_table_renamedContext",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "columns": {"$ref": "#/definitions/Test_table_renamedColumnsContext"},
                        },
                        "required": ["columns"],
                    },
                    "TablesContext": {
                        "title": "TablesContext",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1Context"},
                            "test_table_renamed": {"$ref": "#/definitions/Test_table_renamedContext"},
                        },
                        "required": ["table1", "test_table_renamed"],
                    },
                },
            },
        }
    )


def sync_components_response(app_name: str, page_name: str, token: str):
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
                    "TextContextProperty": {
                        "title": "TextContextProperty",
                        "type": "object",
                        "properties": {"visible": {"title": "Visible", "type": "boolean"}},
                    },
                    "Widget1ComponentsContext": {
                        "title": "Widget1ComponentsContext",
                        "type": "object",
                        "properties": {"text1": {"$ref": "#/definitions/TextContextProperty"}},
                        "required": ["text1"],
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


def sync_table_columns_response(payload: dict):
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
                            "user_id": {"title": "User Id", "type": "string"},
                            "username": {"title": "Username", "type": "string"},
                            "email": {"title": "Email", "type": "string"},
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
                            "user_id": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "username": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "email": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["user_id", "username", "email"],
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


def handle_state_context_updates_response(res: dict):
    return {"message": "success"}


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


def sync_page_response(*args, **kwargs):
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
                    "Widget2State": {"title": "Widget2State", "type": "object", "properties": {}},
                    "WidgetsState": {
                        "title": "WidgetsState",
                        "type": "object",
                        "properties": {"widget2": {"$ref": "#/definitions/Widget2State"}},
                        "required": ["widget2"],
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
                    "Widget2ComponentsContext": {
                        "title": "Widget2ComponentsContext",
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                    "Widget2Context": {
                        "title": "Widget2Context",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "components": {"$ref": "#/definitions/Widget2ComponentsContext"},
                        },
                        "required": ["components"],
                    },
                    "WidgetsContext": {
                        "title": "WidgetsContext",
                        "type": "object",
                        "properties": {"widget2": {"$ref": "#/definitions/Widget2Context"}},
                        "required": ["widget2"],
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
