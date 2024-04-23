import ast
import copy
import importlib
import inspect
import json
import os
import shutil

import astor

from dropbase.helpers.boilerplate import *
from dropbase.helpers.state_context import compose_state_context_models
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

    # def update_base_class(self):
    #     table_base_methods = ""
    #     widget_base_methods = ""
    #     for _, values in self.properties:
    #         if isinstance(values, TableDefinedProperty):
    #             """
    #             table methods are added in TableABC class
    #             here, we only need to add a method if it's a button column
    #             """
    #             for column in values.columns:
    #                 if isinstance(column, ButtonColumnDefinedProperty):
    #                     table_base_methods += button_methods_base.format(column.name)
    #         if isinstance(values, WidgetDefinedProperty):
    #             for component in values.components:
    #                 if isinstance(component, ButtonDefinedProperty):
    #                     widget_base_methods += button_methods_base.format(
    #                         component.name
    #                     )

    #     base_class_str = base_class_base + "\n\n" + "class TableBase(TableABC):\n"
    #     if len(table_base_methods) > 0:
    #         base_class_str += table_base_methods
    #     else:
    #         base_class_str += "    pass\n"

    #     base_class_str += "\n\n" + "class WidgetBase(WidgetABC):\n"
    #     if len(widget_base_methods) > 0:
    #         base_class_str += widget_base_methods
    #     else:
    #         base_class_str += "    pass\n"

    #     with open(self.page_path + "/base_class.py", "w") as f:
    #         f.write(base_class_str)

    def create_main_class(self):
        with open(self.page_path + "/scripts/main.py", "w") as f:
            f.write(main_class_init)

    def get_script_methods(self):
        script_path = f"{self.page_module_path}.scripts.main"
        script_path_module = importlib.import_module(script_path)
        importlib.reload(script_path_module)
        Script = getattr(script_path_module, "Script")
        return [
            m
            for m, f in inspect.getmembers(Script, predicate=inspect.isfunction)
            if f.__module__ == Script.__module__
        ]

    def get_base_methods(self):
        script_path = f"{self.page_module_path}.base_class"
        script_path_module = importlib.import_module(script_path)
        importlib.reload(script_path_module)
        ScriptBase = getattr(script_path_module, "ScriptBase")
        return [method for method in dir(ScriptBase) if not method.startswith("_")]

    def get_base_abstract_methods(self):
        script_path = f"{self.page_module_path}.base_class"
        script_path_module = importlib.import_module(script_path)
        importlib.reload(script_path_module)
        ScriptBase = getattr(script_path_module, "ScriptBase")
        abstract_methods = []
        for name, method in inspect.getmembers(ScriptBase, predicate=inspect.isfunction):
            if hasattr(method, "__isabstractmethod__") and method.__isabstractmethod__:
                abstract_methods.append(name)
        return abstract_methods

    def update_main_class(self):

        required_classes = self.get_require_classes()

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
        # with open("test.py", "w") as f:
        #     f.write(modified_code)

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
        # self.update_base_class()
        self.create_main_class()
        self.add_inits()

    def update_page(self):
        # self.update_schema()
        properties = self.reload_properties()
        compose_state_context_models(self.app_name, self.page_name, properties)
        # self.update_base_class()
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

    def get_require_base_methods(self):
        required_methods = {}
        for key, values in self.properties:
            if isinstance(values, TableDefinedProperty):
                name = f"get_{key}"
                required_methods[name] = update_table_methods_main.format(key)
            if isinstance(values, WidgetDefinedProperty):
                for component in values.components:
                    if isinstance(component, ButtonDefinedProperty):
                        name = f"on_click_{component.name}"
                        required_methods[name] = update_button_methods_main.format(component.name)
        return required_methods
