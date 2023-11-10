# TODO MOCKIFY ME
from server.tests.mocks.util import mock_response

session = 1


def sync_table_columns_response(
    app_name: str, page_name: str, table_columns: dict, token: str, table_type: str
):
    return session.post(
        url="sync/columns/",
        json={
            "app_name": app_name,
            "page_name": page_name,
            "table_columns": table_columns,
            "token": token,
            "table_type": table_type,
        },
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
            "status": "success",
        }
    )


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
            "status": "success",
        }
    )


def get_smart_columns_response(user_sql: str, column_names: list, gpt_schema: dict, db_schema: dict):
    return session.post(
        url="get_smart_cols/",
        json={
            "user_sql": user_sql,
            "column_names": column_names,
            "gpt_schema": gpt_schema,
            "db_schema": db_schema,
        },
    )


def update_smart_columns_response(smart_columns: list, table: dict):
    return session.post(
        url="update_smart_cols/",
        json={
            "smart_columns": smart_columns,
            "table": table,
        },
    )
