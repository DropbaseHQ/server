import time

from fastapi import HTTPException

from dropbase.helpers.display_rules import run_display_rule
from dropbase.helpers.utils import (
    _dict_from_pydantic_model,
    get_empty_context,
    get_state_context_model,
    read_page_properties,
    validate_column_name,
)
from dropbase.schemas.page import PageProperties
from server.controllers.properties import update_properties


def get_page(app_name: str, page_name: str, initial=False):
    page_props = get_page_state_context(app_name, page_name, initial)
    properties = read_page_properties(app_name, page_name)
    page_props["properties"] = properties
    return page_props


def update_page_properties(req: PageProperties):
    try:
        # validate properties
        validate_property_names(req.properties.dict())
        # update properties
        update_properties(req.app_name, req.page_name, req.properties.dict())
        # get new steate and context
        return {"message": "success"}
        # return {"state_context": state_context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def validate_property_names(properties: dict):
    # create a set to track table names
    table_names = set()
    widget_names = set()

    # validate column names
    for block in properties["blocks"]:
        if block["name"] == "page":
            raise Exception("Page is a reserved name")

        if block["block_type"] == "table":
            # Check for duplicate table names
            if block["name"] in table_names:
                raise Exception("A table with this name already exists")

            table_names.add(block["name"])

            if not validate_column_name(block["name"]):
                raise Exception("Invalid table names present in the table")
            for column in block.get("columns"):
                if not validate_column_name(column["name"]):
                    raise Exception("Invalid column names present in the table")
        elif block["block_type"] == "widget":
            if block["name"] in widget_names:
                raise Exception("A widget with this name already exists")

            widget_names.add(block["name"])

            if not validate_column_name(block["name"]):
                raise Exception("Invalid widget names present in the table")

            component_names = set()
            for component in block.get("components"):
                if component["name"] in component_names:
                    raise Exception("A component with this name already exists")

                component_names.add(component["name"])

                if not validate_column_name(component["name"]):
                    raise Exception("Invalid component names present in the table")


def get_state_context(app_name, page_name, permissions, initial=False):
    try:
        state_context = get_page_state_context(app_name, page_name, initial)
        state_context["properties"] = read_page_properties(app_name, page_name)
        return {"state_context": state_context, "permissions": permissions}
    except Exception:
        try:
            # in cases where there are some hanging files/dirs from update properties step
            # wait for a second for files to clear up and try again
            time.sleep(1)
            state_context = get_page_state_context(app_name, page_name)
            state_context["properties"] = read_page_properties(app_name, page_name)
            return {"state_context": state_context, "permissions": permissions}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


def get_page_state_context(app_name: str, page_name: str, initial=False):
    State = get_state_context_model(app_name, page_name, "state")
    state = _dict_from_pydantic_model(State)
    if initial:
        context = get_empty_context(app_name, page_name).dict()
    else:
        context = run_display_rule(app_name, page_name, state)
    return {"state": state, "context": context}
