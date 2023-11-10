from typing import Optional
from uuid import UUID

from server.tests.mocks.util import mock_response


def create_component_response(property: dict, widget_id: UUID, after: Optional[UUID], type: str):
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
                            property["name"]: {
                                "title": property["name"].capitalize(),
                                "default": "str",
                                "type": "string",
                            }
                        },
                    },
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
                            property["name"]: {
                                "$ref": f"#/definitions/{type.capitalize()}ContextProperty"
                            }
                        },
                        "required": [property["name"]],
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


def update_component_response(component_id: str, update_data: dict):
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
                            "text91": {"$ref": "#/definitions/TextContextProperty"},
                            "text1": {"$ref": "#/definitions/TextContextProperty"},
                            "input1": {"$ref": "#/definitions/InputContextProperty"},
                            "select1": {"$ref": "#/definitions/SelectContextProperty"},
                            "button1": {"$ref": "#/definitions/ButtonContextProperty"},
                        },
                        "required": ["text91", "text1", "input1", "select1", "button1"],
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
                        "properties": {"table1": {"$ref": "#/definitions/Table1Context"}},
                        "required": ["table1"],
                    },
                },
            },
            "status": "success",
        }
    )


def delete_component_response(component_id: str):
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
