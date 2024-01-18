import importlib
import json


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
