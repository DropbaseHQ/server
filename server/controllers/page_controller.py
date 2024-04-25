import ast
import json
import os
import shutil

import astor

from dropbase.helpers.boilerplate import *
from dropbase.helpers.state_context import compose_state_context_models, get_page_state_context
from dropbase.helpers.utils import get_page_properties, read_app_properties, read_page_properties
from dropbase.models import *


class PageController:
    def __init__(self, app_name: str, page_name: str) -> None:
        self.app_name = app_name
        self.page_name = page_name
        self.page_path = f"workspace/{self.app_name}/{self.page_name}"
        self.page_module_path = f"workspace.{self.app_name}.{self.page_name}"
        self.properties = None

    def reload_properties(self):
        properties = get_page_properties(self.app_name, self.page_name)
        self.properties = properties
        return self.properties

    def create_page_dirs(self):
        # create page
        os.mkdir(self.page_path)
        # create scripts
        os.mkdir(self.page_path + "/scripts")

    def create_schema(self):
        # create page schema
        with open(self.page_path + "/schema.py", "w") as f:
            f.write(schema_boilerplate_init)

    def create_page_properties(self):
        with open(self.page_path + "/properties.json", "w") as f:
            f.write(properties_json_boilerplate)

    def create_app_init_properties(self):
        # assuming page name is page1 by default
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties_boilerplate, indent=2))

    def add_page_to_app_properties(self, page_label: str):
        app_properties = read_app_properties(self.app_name)
        app_properties[self.page_name] = {"label": page_label}
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties, indent=2))

    def remove_page_from_app_properties(self):
        app_properties = read_app_properties(self.app_name)
        app_properties.pop(self.page_name)
        with open(f"workspace/{self.app_name}/properties.json", "w") as f:
            f.write(json.dumps(app_properties, indent=2))

    def update_page_properties(self, properties: dict):
        """
        NOTE: properties are not validated against Properties schema since
        if component is removed from incoming properties, Properties will fail the validation
        """

        # write properties to file
        with open(self.page_path + "/properties.json", "w") as f:
            f.write(json.dumps(properties, indent=2))

        # update schema
        self.update_page()

    def create_main_class(self):
        with open(self.page_path + "/scripts/main.py", "w") as f:
            f.write(main_class_init)

    def update_main_class(self):

        required_classes = self.get_require_classes()
        required_methods = self.get_required_methods()

        file_path = self.page_path + "/scripts/main.py"

        # Parse the existing code
        with open(file_path, "r") as f:
            module = ast.parse(f.read())

        visited_classes = []
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                visited_classes.append(node.name)
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC":
                        # make sure get_table is defined
                        get_data_present = "get_data" in [n.name for n in node.body]
                        if not get_data_present:
                            new_method_node = ast.parse(get_data_template).body[0]
                            node.body.append(new_method_node)

                    if base_name == "TableABC" or base_name == "WidgetABC":
                        if node.name not in required_methods:
                            continue
                        # iterate over methods in the node
                        class_methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        for method in required_methods[node.name]:
                            if method not in class_methods:
                                new_method_node = ast.parse(required_methods[node.name][method]).body[0]
                                node.body.append(new_method_node)

                # remove pass statements from class
                if any(isinstance(child, ast.Pass) for child in node.body) and len(node.body) > 1:
                    node.body = [n for n in node.body if not isinstance(n, ast.Pass)]

        # add missing classes
        for req_class in required_classes:
            if req_class not in visited_classes:
                new_class_node = ast.parse(required_classes[req_class]).body[0]
                module.body.append(new_class_node)

        # removed deleted classes
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC" or base_name == "WidgetABC":
                        if node.name not in required_classes:
                            print("removing ", node.name)
                            module.body.remove(node)

        modified_code = astor.to_source(module)
        with open(file_path, "w") as f:
            f.write(modified_code)

    def add_inits(self):
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
        # TODO: validate columns here
        properties = read_page_properties(self.app_name, self.page_name)
        filepath = f"workspace/{self.app_name}/{self.page_name}/properties.json"
        properties.get(table_name)["columns"] = columns
        with open(filepath, "w") as f:
            f.write(json.dumps(properties, indent=2))

    def create_page(self, page_label: str):
        self.create_page_dirs()
        self.create_schema()
        self.create_page_properties()
        self.add_page_to_app_properties(page_label)
        properties = self.reload_properties()
        compose_state_context_models(self.app_name, self.page_name, properties)
        self.create_main_class()
        self.add_inits()

    def update_page(self):
        properties = self.reload_properties()
        compose_state_context_models(self.app_name, self.page_name, properties)
        self.update_main_class()

    def delete_page(self):
        page_folder_path = f"workspace/{self.app_name}/{self.page_name}"
        shutil.rmtree(page_folder_path)
        self.remove_page_from_app_properties()

    def get_require_classes(self):
        required_classes = {}
        for key, values in self.properties:
            class_name = key.capitalize()
            if isinstance(values, TableDefinedProperty):
                required_classes[class_name] = table_class_boilerplate.format(class_name)
            if isinstance(values, WidgetDefinedProperty):
                required_classes[class_name] = widget_class_boilerplate.format(class_name)
        return required_classes

    def get_required_methods(self):
        required_methods = {}
        for key, values in self.properties:
            class_name = key.capitalize()
            if isinstance(values, TableDefinedProperty):
                for columns in values.columns:
                    # loop through columns and check if they are buttons
                    if isinstance(columns, ButtonColumnDefinedProperty):
                        if class_name not in required_methods:
                            required_methods[class_name] = {}
                        name = f"on_click_{columns.name}"
                        required_methods[class_name][name] = update_button_methods_main.format(
                            columns.name
                        )
            if isinstance(values, WidgetDefinedProperty):
                for component in values.components:
                    # loop through components and check if they are buttons
                    if isinstance(component, ButtonDefinedProperty):
                        if class_name not in required_methods:
                            required_methods[class_name] = {}
                        name = f"on_click_{component.name}"
                        required_methods[class_name][name] = update_button_methods_main.format(
                            component.name
                        )
        return required_methods

    def get_page(self, initial=False):
        self.reload_properties()
        response = get_page_state_context(self.app_name, self.page_name, initial)
        # get methods
        response["properties"] = self.properties
        response["methods"] = self.get_main_class_methods()
        return response

    def get_main_class_methods(self):
        file_path = self.page_path + "/scripts/main.py"
        with open(file_path, "r") as f:
            module = ast.parse(f.read())

        class_methods = {}
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC":
                        class_name = node.name.lower()
                        for n in node.body:
                            if isinstance(n, ast.FunctionDef):
                                if class_name not in class_methods:
                                    class_methods[class_name] = {
                                        "columns": {},
                                        "header": {},
                                        "footer": {},
                                        "methods": [],
                                    }
                                # parse component methods
                                parse_component_methods(n.name, class_name, class_methods, "table")
                                # parse table methods
                                if n.name in ["get_data", "update", "delete", "add"]:
                                    class_methods[class_name]["methods"].append(n.name)

                    if base_name == "WidgetABC":
                        class_name = node.name.lower()
                        for n in node.body:
                            if isinstance(n, ast.FunctionDef):
                                if class_name not in class_methods:
                                    class_methods[class_name] = {"components"}
                                # parse component methods
                                parse_component_methods(n.name, class_name, class_methods, "widget")

        return class_methods


# helper functions
def parse_component_methods(method_name: str, class_name: str, class_methods: dict, class_type: str):
    # check header
    sections = ["header", "footer", "columns"] if class_type == "table" else ["components"]
    methods = ["on_click", "on_select", "on_toggle", "on_submit"]
    for section in sections:
        if method_name.startswith(f"{section}_"):
            for method in methods:
                if method_name.endswith(f"_{method}"):
                    component_name = method_name.split(f"{section}_")[1].split(f"_{method}")[0]
                    if component_name not in class_methods[class_name][section]:
                        class_methods[class_name][section][component_name] = []
                    class_methods[class_name][section][component_name].append(method)
