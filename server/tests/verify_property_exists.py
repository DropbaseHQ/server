import json

from dropbase.helpers.utils import read_page_properties


def get_value_from_json_path(data, json_path):
    keys = json_path.split(".")
    for key in keys:
        if "[" in key and "]" in key:
            key, index = key.split("[")
            index = int(index[:-1])
            data = data.get(key, [])[index]
        else:
            data = data.get(key)
        if data is None:
            return None
    return data


def verify_property_exists(
    attribute_path: str,
    attribute_value: str,
    app_name: str = "dropbase_test_app",
    page_name: str = "page1",
) -> bool:
    file_name = "properties.json"
    file_path = f"workspace/{app_name}/{page_name}/{file_name}"

    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        value = get_value_from_json_path(data, attribute_path)
        return value == attribute_value

    except ImportError as e:
        print(f"Error importing module: {e}")
        return False
    except AttributeError as e:
        print(f"Error accessing class: {e}")
        return False


def verify_object_prop_exists(app_name, page_name, comp_type, comp_name, attribute):
    properties = read_page_properties(app_name, page_name)
    for block in properties["blocks"]:
        if block["block_type"] == comp_type and block["name"] == comp_name:
            return block[attribute]


def get_objects_child_prop(properties, comp_type, comp_name, child_type, child_name, attribute):  # noqa
    for block in properties["blocks"]:
        if block["block_type"] == comp_type and block["name"] == comp_name:
            for child in block[child_type]:
                if child["name"] == child_name:
                    return child[attribute]
    return None


def verify_object_exists(app_name, page_name, comp_type, comp_name):
    properties = read_page_properties(app_name, page_name)
    for block in properties["blocks"]:
        if block["block_type"] == comp_type and block["name"] == comp_name:
            return True
    return False
