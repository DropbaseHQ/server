from pydantic import BaseModel

from server.controllers.display_rules import run_display_rule
from server.controllers.generate_models import create_state_context_files
from server.controllers.utils import (
    get_state_context_model,
    read_page_properties,
    validate_column_name,
    write_page_properties,
)
from server.schemas.page import PageProperties


def update_page_properties(req: PageProperties):
    # TODO: revert to prev version if failed
    # validate properties
    validate_property(req.properties.dict())

    # to update depends on flags in properties.json
    properties = read_page_properties(req.app_name, req.page_name)
    # check for a data fetcher is bound to a table
    check_data_fetcher_bound_to_table(properties, req.properties.dict())

    # write properties
    write_page_properties(**req.dict())
    # update state context
    create_state_context_files(**req.dict())
    # get new steate and context
    return get_page_state_context(req.app_name, req.page_name)


def validate_property(properties: dict):
    # validate column names
    for table in properties["tables"]:
        if not validate_column_name(table["name"]):
            raise Exception("Invalid table names present in the table")
        for column in table.get("columns"):
            if not validate_column_name(column["name"]):
                raise Exception("Invalid column names present in the table")
    # validate component names
    for widget in properties["widgets"]:
        if not validate_column_name(widget["name"]):
            raise Exception("Invalid widget names present in the table")
        for component in widget.get("components"):
            if not validate_column_name(component["name"]):
                raise Exception("Invalid component names present in the table")


def check_data_fetcher_bound_to_table(current_propertirs: dict, incoming_properties: dict):
    # check if data fetcher has changes
    current_tables = {table["name"]: table for table in current_propertirs["tables"]}
    current_files = {file["name"]: file for file in current_propertirs["files"]}
    for table in incoming_properties["tables"]:
        if table["name"] in current_tables.keys():
            if table.get("fetcher") != current_tables[table["name"]].get("fetcher"):
                if current_files[table.get("fetcher")].get("type") == "sql":
                    # update depends on flags in properties.json
                    # depends_on = get_sql_variables(user_sql=req.sql)
                    # tbc
                    pass


def get_page_state_context(app_name: str, page_name: str):
    State = get_state_context_model(app_name, page_name, "state")
    Context = get_state_context_model(app_name, page_name, "context")
    state = _dict_from_pydantic_model(State)
    context = _dict_from_pydantic_model(Context)
    context = run_display_rule(app_name, page_name, state, context)
    return {"state": state, "context": context}


def _dict_from_pydantic_model(model):
    data = {}
    for name, field in model.__fields__.items():
        if isinstance(field.outer_type_, type) and issubclass(field.outer_type_, BaseModel):
            data[name] = _dict_from_pydantic_model(field.outer_type_)
        else:
            data[name] = field.default
    return data
