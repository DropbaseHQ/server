import ast
import json
import os
import re
import shutil

import astor

from dropbase.helpers.boilerplate import *
from dropbase.helpers.state_context import compose_state_context_models, get_page_state_context
from dropbase.helpers.utils import (
    get_page_properties,
    read_app_properties,
    read_page_properties,
    validate_page_properties,
)
from dropbase.models import *

prefixes = ["header", "footer", "columns", "components"]
suffixes = ["on_click", "on_select", "on_toggle", "on_submit"]

# Join prefixes and suffixes to form a regex pattern
prefix_pattern = "|".join(re.escape(prefix) for prefix in prefixes)
suffix_pattern = "|".join(re.escape(suffix) for suffix in suffixes)

# Compile the complete regex pattern
pattern = re.compile(f"^({prefix_pattern})_(.*?)_({suffix_pattern})$")


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
        with open(self.page_path + "/script.py", "w") as f:
            f.write(sctipt_boilerplate_init)

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
        validate_page_properties(properties)
        # write properties to file
        with open(self.page_path + "/properties.json", "w") as f:
            f.write(json.dumps(properties, indent=2))

        # update schema
        self.update_page()

    def create_main_class(self):
        main_class_init_str = main_class_init.format(self.app_name, self.page_name)
        with open(self.page_path + "/scripts/main.py", "w") as f:
            f.write(main_class_init_str)

    def update_main_class(self):

        required_classes = self._get_require_classes()
        required_methods = self._get_required_methods()

        file_path = self.page_path + "/scripts/main.py"

        # Parse the existing code
        with open(file_path, "r") as f:
            module = ast.parse(f.read())

        visited_classes = []

        # add missing methods
        self._add_missing_methods(module, required_methods, visited_classes)

        # remove deleted methods
        self._remove_deleted_methods(module)

        # add missing classes
        self._add_missing_classes(module, required_classes, visited_classes)

        # removed deleted classes
        self._remove_deleted_classes(module, required_classes)

        modified_code = astor.to_source(module)
        with open(file_path, "w") as f:
            f.write(modified_code)

        # format with black
        os.system(f"black {file_path}")

    def _add_missing_methods(self, module, required_methods, visited_classes):
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                visited_classes.append(node.name)
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC":
                        # make sure get_table is defined
                        function_names = [n.name for n in node.body]
                        for method in ["get", "add", "update", "delete", "on_row_change"]:
                            if method not in function_names:
                                new_method_node = ast.parse(table_method_templates.get(method)).body[0]
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

    def _remove_deleted_methods(self, module):
        properties = read_page_properties(self.app_name, self.page_name)
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC" or base_name == "WidgetABC":
                        block_name = node.name.lower()
                        # make sure get_table is defined
                        for method in node.body:
                            # if it's not a method, skip
                            if not isinstance(method, ast.FunctionDef):
                                continue

                            # find methods that match the pattern components_name_on_click
                            match = pattern.match(method.name)

                            # if found, confirm it's present in properties.json
                            if match:
                                section, comp_name = match.group(1), match.group(2)
                                # section would be header, footer, columns, components
                                # comp_name would be the name of the component
                                if block_name in properties:
                                    if section in properties[block_name]:
                                        # get all component names in the section
                                        component_names = [
                                            c["name"] for c in properties[block_name][section]
                                        ]
                                        if comp_name not in component_names:
                                            """
                                            if function is present in main.py but component is not
                                            in properties.json, then remove method from module
                                            """
                                            node.body.remove(method)

                    # if all the methods are removed, add a pass statement to the class
                    if not any(
                        isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Pass))
                        for member in node.body
                    ):
                        # Add a `pass` statement if the class is empty
                        node.body.append(ast.Pass())

    def _add_missing_classes(self, module, required_classes, visited_classes):
        for req_class in required_classes:
            if req_class not in visited_classes:
                new_class_node = ast.parse(required_classes[req_class]).body[0]
                module.body.append(new_class_node)

    def _remove_deleted_classes(self, module, required_classes):
        for node in module.body:
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = base.attr if isinstance(base, ast.Attribute) else base.id
                    if base_name == "TableABC" or base_name == "WidgetABC":
                        if node.name not in required_classes:
                            module.body.remove(node)

    def add_inits(self):
        with open(f"workspace/{self.app_name}/__init__.py", "w") as f:
            f.write(app_init_boilerplate)

        page_init_boilerplate_str = page_init_boilerplate.format(self.app_name, self.page_name)
        with open(self.page_path + "/__init__.py", "w") as f:
            f.write(page_init_boilerplate_str)

    def save_table_columns(self, table_name: str, columns: list):
        # update page properties file
        self.update_table_columns(table_name, columns)
        # update page scripts
        self.update_page()

    def update_table_columns(self, table_name: str, columns: list):
        # TODO: validate columns here
        properties = read_page_properties(self.app_name, self.page_name)
        properties.get(table_name)["columns"] = columns
        validate_page_properties(properties)
        filepath = f"workspace/{self.app_name}/{self.page_name}/properties.json"
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

    def _get_require_classes(self):
        """
        returns a dictionary with table and widget classes that are required along with
        their boilerplate code
        {
            "Table1": "class Table1(TableABC):...",
        }
        """
        required_classes = {}
        for key, values in self.properties:
            class_name = key.capitalize()
            if isinstance(values, TableProperty):
                required_classes[class_name] = table_class_boilerplate.format(class_name, key)
            if isinstance(values, WidgetProperty):
                required_classes[class_name] = widget_class_boilerplate.format(class_name)
        return required_classes

    def _get_required_methods(self):
        required_methods = {}
        for key, values in self.properties:
            class_name = key.capitalize()
            if isinstance(values, TableProperty):
                for column in values.columns:
                    add_button_method(column, "columns", class_name, required_methods)
                for component in values.header:
                    add_button_method(component, "header", class_name, required_methods)
                for component in values.footer:
                    add_button_method(component, "footer", class_name, required_methods)
            if isinstance(values, WidgetProperty):
                for component in values.components:
                    add_button_method(component, "components", class_name, required_methods)
        return required_methods

    def get_page(self, initial=False):
        self.reload_properties()
        response = get_page_state_context(self.app_name, self.page_name, initial)
        if initial:
            # set first widget visibility to true
            set_widget_visibility(response)
        # get methods
        response["properties"] = self.properties
        response["methods"] = self.get_main_class_methods()
        return response

    def get_methods(self):
        return self.get_main_class_methods()

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
                            if isinstance(n, ast.FunctionDef) and not is_simple_return_context(n):
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
                                if n.name in ["get", "add", "update", "delete", "on_row_change"]:
                                    class_methods[class_name]["methods"].append(n.name)

                    if base_name == "WidgetABC":
                        class_name = node.name.lower()
                        for n in node.body:
                            if isinstance(n, ast.FunctionDef) and not is_simple_return_context(n):
                                if class_name not in class_methods:
                                    class_methods[class_name] = {"components": {}}
                                # parse component methods
                                parse_component_methods(n.name, class_name, class_methods, "widget")

        return class_methods


def is_simple_return_context(node):
    """
    Check if the function node consists only of a single return context statement.
    """
    if len(node.body) == 1:
        stmt = node.body[0]
        if (
            isinstance(stmt, ast.Return)
            and isinstance(stmt.value, ast.Name)
            and stmt.value.id == "context"
        ):
            return True
    return False


def add_button_method(component, section, class_name, required_methods):
    # loop through components and check if they are buttons
    if isinstance(
        component,
        (
            ButtonProperty,
            ButtonColumnProperty,
            InputProperty,
            SelectProperty,
            BooleanProperty,
        ),
    ):
        if class_name not in required_methods:
            required_methods[class_name] = {}
        if isinstance(component, (ButtonProperty, ButtonColumnProperty)):
            name = f"{section}_{component.name}_on_click"
        if isinstance(component, InputProperty):
            name = f"{section}_{component.name}_on_submit"
        if isinstance(component, SelectProperty):
            name = f"{section}_{component.name}_on_select"
        if isinstance(component, BooleanProperty):
            name = f"{section}_{component.name}_on_toggle"
        required_methods[class_name][name] = update_button_methods_main.format(name)


def set_widget_visibility(response):
    if "widget1" in response["context"]:
        response["context"]["widget1"]["visible"] = True
    else:
        for _, value in response["context"].items():
            if "components" in value:
                value["visible"] = True
                break


# helper functions
def parse_component_methods(method_name: str, class_name: str, class_methods: dict, class_type: str):
    # check header
    # TODO: refactor this to use regex
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
