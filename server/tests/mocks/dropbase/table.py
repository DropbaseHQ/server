from server.tests.mocks.util import mock_response


def create_table_response(page_id: str, name: str, property: str, depends_on: str):
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
                        "properties": {
                            "input1": {"title": "Input1", "default": "str", "type": "string"},
                            "select1": {"title": "Select1", "default": "str", "type": "string"},
                        },
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
                    "Test_tableState": {"title": "Test tableState", "type": "object", "properties": {}},
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1State"},
                            "test_table": {"$ref": "#/definitions/Test_tableState"},
                        },
                        "required": ["table1", "test_table"],
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
                    "InputContextProperty": {
                        "title": "InputContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "value": {"title": "Value", "type": "string"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "SelectContextProperty": {
                        "title": "SelectContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "value": {"title": "Value", "type": "string"},
                            "options": {
                                "title": "Options",
                                "category": "Default",
                                "type": "array",
                                "items": {"type": "object"},
                            },
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "ButtonContextProperty": {
                        "title": "ButtonContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "Widget1ComponentsContext": {
                        "title": "Widget1ComponentsContext",
                        "type": "object",
                        "properties": {
                            "text1": {"$ref": "#/definitions/TextContextProperty"},
                            "input1": {"$ref": "#/definitions/InputContextProperty"},
                            "select1": {"$ref": "#/definitions/SelectContextProperty"},
                            "button1": {"$ref": "#/definitions/ButtonContextProperty"},
                        },
                        "required": ["text1", "input1", "select1", "button1"],
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
                    "Test_tableColumnsContext": {
                        "title": "Test tableColumnsContext",
                        "type": "object",
                        "properties": {},
                    },
                    "Test_tableContext": {
                        "title": "Test_tableContext",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "columns": {"$ref": "#/definitions/Test_tableColumnsContext"},
                        },
                        "required": ["columns"],
                    },
                    "TablesContext": {
                        "title": "TablesContext",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1Context"},
                            "test_table": {"$ref": "#/definitions/Test_tableContext"},
                        },
                        "required": ["table1", "test_table"],
                    },
                },
            },
            "status": "success",
        }
    )


def update_table_response(table_id: str, update_data: dict):
    # FIXME dropbase api does not have update table endpoint as of Nov 7 2023
    raise NotImplementedError


def update_table_property_response(table_id: str, update_data: dict, depends_on=None):
    return mock_response(
        json={
            "name": update_data["name"],
            "property": update_data["property"],
            "page_id": update_data["page_id"],
            "date": "2023-11-07T22:14:14.844164",
            "file_id": update_data["file_id"],
            "id": table_id,
            "depends_on": depends_on,
        }
    )


def update_table_columns_response(table_id: str, update_data: dict):
    return mock_response(
        json={
            "app_name": "yahoo",
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
                        "properties": {
                            "input1": {"title": "Input1", "default": "str", "type": "string"},
                            "select1": {"title": "Select1", "default": "str", "type": "string"},
                        },
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
                    "BruhState": {
                        "title": "BruhState",
                        "type": "object",
                        "properties": {
                            "test": {"title": "Test", "default": "str", "type": "string"},
                            "bruh": {"title": "Bruh", "default": "str", "type": "string"},
                        },
                    },
                    "TablesState": {
                        "title": "TablesState",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1State"},
                            "bruh": {"$ref": "#/definitions/BruhState"},
                        },
                        "required": ["table1", "bruh"],
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
                    "InputContextProperty": {
                        "title": "InputContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "value": {"title": "Value", "type": "string"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "SelectContextProperty": {
                        "title": "SelectContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "value": {"title": "Value", "type": "string"},
                            "options": {
                                "title": "Options",
                                "category": "Default",
                                "type": "array",
                                "items": {"type": "object"},
                            },
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "ButtonContextProperty": {
                        "title": "ButtonContextProperty",
                        "type": "object",
                        "properties": {
                            "visible": {"title": "Visible", "type": "boolean"},
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                        },
                    },
                    "Widget1ComponentsContext": {
                        "title": "Widget1ComponentsContext",
                        "type": "object",
                        "properties": {
                            "text1": {"$ref": "#/definitions/TextContextProperty"},
                            "input1": {"$ref": "#/definitions/InputContextProperty"},
                            "select1": {"$ref": "#/definitions/SelectContextProperty"},
                            "button1": {"$ref": "#/definitions/ButtonContextProperty"},
                        },
                        "required": ["text1", "input1", "select1", "button1"],
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
                    "BruhColumnsContext": {
                        "title": "BruhColumnsContext",
                        "type": "object",
                        "properties": {
                            "test": {"$ref": "#/definitions/PgColumnContextProperty"},
                            "bruh": {"$ref": "#/definitions/PgColumnContextProperty"},
                        },
                        "required": ["test", "bruh"],
                    },
                    "BruhContext": {
                        "title": "BruhContext",
                        "type": "object",
                        "properties": {
                            "message": {"title": "Message", "type": "string"},
                            "message_type": {"title": "Message Type", "type": "string"},
                            "columns": {"$ref": "#/definitions/BruhColumnsContext"},
                        },
                        "required": ["columns"],
                    },
                    "TablesContext": {
                        "title": "TablesContext",
                        "type": "object",
                        "properties": {
                            "table1": {"$ref": "#/definitions/Table1Context"},
                            "bruh": {"$ref": "#/definitions/BruhContext"},
                        },
                        "required": ["table1", "bruh"],
                    },
                },
            },
            "status": "success",
        }
    )


def delete_table_response(*args, **kwargs):
    # not implemented
    return mock_response(json={})
