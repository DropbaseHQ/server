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
        self._backup_and_write(self.page_path + "/schema.py", schema_boilerplate_init)

    def create_page_properties(self):
        self._backup_and_write(self.page_path + "/properties.json", properties_json_boilerplate)

    def create_app_init_properties(self):
        # assuming page name is page1 by default
        self._backup_and_write(
            f"workspace/{self.app_name}/properties.json",
            json.dumps(app_properties_boilerplate, indent=2),
        )

    def add_page_to_app_properties(self, page_label: str):
        app_properties = read_app_properties(self.app_name)
        app_properties[self.page_name] = {"label": page_label}
        self._backup_and_write(
            f"workspace/{self.app_name}/properties.json", json.dumps(app_properties, indent=2)
        )

    def remove_page_from_app_properties(self):
        app_properties = read_app_properties(self.app_name)
        app_properties.pop(self.page_name)
        self._backup_and_write(
            f"workspace/{self.app_name}/properties.json", json.dumps(app_properties, indent=2)
        )

    def update_page_properties(self, properties: dict):
        """
        NOTE: properties are not validated against Properties schema since
        if component is removed from incoming properties, Properties will fail the validation
        """

        self._backup_and_write(self.page_path + "/properties.json", json.dumps(properties, indent=2))

        # update schema
        self.update_page()

    def create_main_class(self):
        self._backup_and_write(self.page_path + "/scripts/main.py", main_class_init)

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
        self._backup_and_write(file_path, modified_code)

    def add_inits(self):
        self._backup_and_write(f"workspace/{self.app_name}/__init__.py", app_init_boilerplate)
        self._backup_and_write(self.page_path + "/__init__.py", page_init_boilerplate)

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

        self._backup_and_write(filepath, page_init_boilerplate)

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
                    if base_name in ["TableABC", "WidgetABC"]:
                        class_name = node.name.lower()
                        for n in node.body:
                            if isinstance(n, ast.FunctionDef):
                                if class_name not in class_methods:
                                    class_methods[class_name] = {}

                                # check for base component methods
                                parse_component_methods(n.name, "on_click_", class_name, class_methods)
                                parse_component_methods(n.name, "on_select_", class_name, class_methods)
                                parse_component_methods(n.name, "on_enter_", class_name, class_methods)

                                # check for base table methods
                                # get data, udpate, delete, add
                                if n.name in ["get_data", "update", "delete", "add"]:
                                    if "methods" not in class_methods[class_name]:
                                        class_methods[class_name]["methods"] = []
                                    class_methods[class_name]["methods"].append(n.name)

        return class_methods

    def _backup_and_write(self, file, contents):
        backup_path = f"{self.page_path}_backup"

        # create a backup by copying entire directory (including subdirectories)
        shutil.copytree(self.page_path, backup_path)

        try:
            # write properties to file
            with open(file, "w") as f:
                f.write(contents)
        except Exception as e:
            # on failure, delete edited directory
            shutil.rmtree(self.page_path)
            # rename backup directory to original name
            os.rename(backup_path, self.page_path)
            raise e
        finally:
            # if no exception occurred, you can remove the backup
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)


# helper functions
def parse_component_methods(method_name: str, method_type: str, class_name: str, class_methods: dict):
    if method_type in method_name:
        component_name = method_name.split(method_type)[1]
        if component_name not in class_methods[class_name]:
            class_methods[class_name][component_name] = []
        class_methods[class_name][component_name].append(method_type)
