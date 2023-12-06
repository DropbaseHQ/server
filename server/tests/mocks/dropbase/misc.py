# TODO MOCKIFY ME
from server.tests.mocks.util import mock_response

session = 1


def sync_table_columns_response(payload: dict):
    table_id = payload["table_id"]
    columns = payload["columns"]
    type = payload["type"]
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
                        "properties": {
                            "test_column": {"title": "test_column", "default": "str", "type": "string"},
                        },
                    },
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1State"},
                        },
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
                            "test_column": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["test_column"],
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
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1Context"},
                        },
                        "required": ["table1"],
                    },
                },
            }
        }
    )


def get_smart_columns_response(*args, **kwargs):
    return mock_response(
        json={
            "columns": {
                "id": {
                    "name": "id",
                    "type": "VARCHAR",
                    "schema_name": "public",
                    "table_name": "users",
                    "column_name": "id",
                    "primary_key": True,
                    "foreign_key": False,
                    "default": None,
                    "nullable": False,
                    "unique": True,
                    "edit_keys": [],
                    "editable": False,
                    "visible": True,
                },
                "name": {
                    "name": "name",
                    "type": "VARCHAR",
                    "schema_name": "public",
                    "table_name": "users",
                    "column_name": "name",
                    "primary_key": False,
                    "foreign_key": False,
                    "default": None,
                    "nullable": True,
                    "unique": False,
                    "edit_keys": ["id"],
                    "editable": False,
                    "visible": True,
                }
            }
        }
    )


def update_smart_columns_response(*args, **kwargs):
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
                        "properties": {
                            "id": {"title": "Id", "default": "str", "type": "string"},
                            "name": {"title": "Name", "default": "str", "type": "string"},
                        },
                    },
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1State"},
                        },
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
                            "id": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "name": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["id", "name"],
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
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1Context"},
                        },
                        "required": ["table1"],
                    },
                },
            }
        }
    )
