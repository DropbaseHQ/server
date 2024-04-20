import ast
import copy
import json
import os
import shutil

import astor

from dropbase.helpers.boilerplate import *
from dropbase.helpers.scriptABC import compose_state_context_models
from dropbase.helpers.utils import (
    get_page_properties,
    get_page_properties_schema,
    read_app_properties,
    read_page_properties,
)
from dropbase.models import *


class PageController:
    def __init__(self, app_name: str, page_name: str) -> None:
        self.app_name = app_name
        self.page_name = page_name
        self.page_path = f"workspace/{self.app_name}/{self.page_name}"
        self.page = None

    def reload_page(self):
        page = get_page_properties(self.app_name, self.page_name)
        self.page = page
        return self.page

    def create_dirs(self, create_app=False):
        if create_app:
            # create app
            os.mkdir(f"workspace/{self.app_name}")
        # create page
        os.mkdir(self.page_path)
        # create scripts
        os.mkdir(self.page_path + "/scripts")

    def create_schema(self):
        # create page schema
        with open(self.page_path + "/schema.py", "w") as f:
            f.write(schema_boilerplate)

    def update_schema(self):
        boilerplate = copy.copy(schema_boilerplate_create)
        # add properties
        for key, value in self.page:
            if isinstance(value, WidgetDefinedProperty):
                class_name = "WidgetDefinedProperty"
            if isinstance(value, TableDefinedProperty):
                class_name = "TableDefinedProperty"
            boilerplate += f"    {key}: {class_name}\n"

        # write file
        with open(self.page_path + "/schema.py", "w") as f:
            f.write(boilerplate)

    def create_page_properties(self):
        with open(self.page_path + "/properties.json", "w") as f:
            f.write(properties_json_boilerplate)

    def create_app_init_properties(self):
        # assuming page name is page1 by default
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties_boilerplate))

    def update_page_to_app_properties(self, page_label: str):
        app_properties = read_app_properties(self.app_name)
        app_properties[self.page_name] = {"label": page_label}
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties))

    def remove_page_from_app_properties(self):
        app_properties = read_app_properties(self.app_name)
        app_properties.pop(self.page_name)
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties))

    def update_properties(self, properties: dict):
        # assert properties are valid
        Properties = get_page_properties_schema(self.app_name, self.page_name)
        Properties(**properties)

        # write properties to file
        with open(self.page_path + "/properties.json", "w") as f:
            f.write(json.dumps(properties))

        # update schema
        self.update_page()

    def update_base_class(self):
        base_methods = ""
        for key, values in self.page:
            if isinstance(values, TableDefinedProperty):
                base_methods += table_methods_base.format(key)
            if isinstance(values, WidgetDefinedProperty):
                for component in values.components:
                    if isinstance(component, ButtonDefinedProperty):
                        base_methods += button_methods_base.format(component.name)
                    elif isinstance(component, InputDefinedProperty):
                        base_methods += input_methods_base.format(component.name)

        base_class_str = base_class.format(base_methods)

        with open(self.page_path + "/base_class.py", "w") as f:
            f.write(base_class_str)

    def create_main_class(self):
        user_methods = ""
        for key, values in self.page:
            if isinstance(values, TableDefinedProperty):
                user_methods += table_methods_main.format(key)
            if isinstance(values, WidgetDefinedProperty):
                for component in values.components:
                    if isinstance(component, ButtonDefinedProperty):
                        user_methods += button_methods_main.format(component.name)
                    elif isinstance(component, InputDefinedProperty):
                        user_methods += input_methods_main.format(component.name)

        main_class_str = main_class.format(user_methods)

        with open(self.page_path + "/scripts/main.py", "w") as f:
            f.write(main_class_str)

    def update_main_class(self):

        incoming_methods = get_incoming_methods(self.page)

        file_path = self.page_path + "/scripts/main.py"

        # Parse the existing code
        with open(file_path, "r") as f:
            module = ast.parse(f.read())

        # get existing methods
        for node in module.body:
            if isinstance(node, ast.ClassDef) and node.name == "Page":
                existing_methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

        # compare existing methods with incoming methods
        for node in module.body:
            if isinstance(node, ast.ClassDef) and node.name == "Page":
                # Remove methods in existing_methods but not in incoming_methods
                node.body = [
                    n
                    for n in node.body
                    if not (
                        isinstance(n, ast.FunctionDef)
                        and n.name in existing_methods
                        and n.name not in incoming_methods
                    )
                ]
                # Check for methods to add
                for method_name, method_body in incoming_methods.items():
                    method_exists = any(
                        isinstance(n, ast.FunctionDef) and n.name == method_name for n in node.body
                    )
                    # Add method if it doesn't exist
                    if not method_exists:
                        # Create a dummy FunctionDef node
                        new_method_node = ast.parse(method_body).body[0]
                        node.body.append(new_method_node)

        modified_code = astor.to_source(module)

        with open(file_path, "w") as f:
            f.write(modified_code)

    def add_init(self):
        with open(f"workspace/{self.app_name}/__init__.py", "w") as f:
            f.write(app_init_boilerplate)

        with open(self.page_path + "/__init__.py", "w") as f:
            f.write(page_init_boilerplate)

    def save_table_columns(self, table_name: str, columns: list):
        # update page properties file
        self.update_table_columns(table_name, columns)
        # update page scripts
        self.update_page()

    def update_table_columns(self, table_name: str, columns: list):
        properties = read_page_properties(self.app_name, self.page_name)
        filepath = f"workspace/{self.app_name}/{self.page_name}/properties.json"
        properties.get(table_name)["columns"] = columns
        with open(filepath, "w") as f:
            f.write(json.dumps(properties))

    def create_app(self):
        self.create_dirs(create_app=True)
        self.create_page_properties()
        self.create_app_init_properties()
        self.create_schema()
        page = self.reload_page()
        compose_state_context_models(self.app_name, self.page_name, page)
        self.update_base_class()
        self.create_main_class()
        self.add_init()

    def create_page(self, page_label: str):
        self.create_dirs()
        self.create_schema()
        self.create_page_properties()
        self.update_page_to_app_properties(page_label)
        page = self.reload_page()
        compose_state_context_models(self.app_name, self.page_name, page)
        self.update_base_class()
        self.create_main_class()
        self.add_init()

    def update_page(self):
        page = self.reload_page()
        self.update_schema()
        compose_state_context_models(self.app_name, self.page_name, page)
        self.update_base_class()
        self.update_main_class()

    def delete_page(self):
        page_folder_path = f"workspace/{self.app_name}/{self.page_name}"
        shutil.rmtree(page_folder_path)
        self.remove_page_from_app_properties()


def get_incoming_methods(page):
    incoming_methods = {}
    for key, values in page:
        if isinstance(values, TableDefinedProperty):
            name = f"get_{key}"
            incoming_methods[name] = update_table_methods_main.format(key)
        if isinstance(values, WidgetDefinedProperty):
            for component in values.components:
                if isinstance(component, ButtonDefinedProperty):
                    name = f"on_click_{component.name}"
                    incoming_methods[name] = update_button_methods_main.format(component.name)
                elif isinstance(component, InputDefinedProperty):
                    name = f"on_enter_{component.name}"
                    incoming_methods[name] = update_input_methods_main.format(component.name)
    return incoming_methods
