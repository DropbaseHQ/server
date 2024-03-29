def get_requried_fields(schema, definitions):
    properties = schema["properties"]
    required = schema.get("required") or []
    refs = {}
    for key, value in properties.items():
        if key in required:
            if "$ref" in value:
                model_name = value["$ref"].split("#/definitions/")[1]
                child_schema = definitions.get(model_name)
                refs[key] = get_requried_fields(child_schema, definitions)
            else:
                refs[key] = pydantic_python_type_mapper[value.get("type")]
    return refs


pydantic_python_type_mapper = {"string": "", "array": [], "object": {}, "integer": 0, "flaot": 0}


def non_empty_values(d):
    non_empty = {}
    for k, v in d.items():
        if isinstance(v, dict):
            nested = non_empty_values(v)
            if nested:
                non_empty[k] = nested
        elif v:  # for Pythonic boolean check
            non_empty[k] = v
    return non_empty
