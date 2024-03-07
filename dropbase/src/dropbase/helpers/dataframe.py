import json

import pandas as pd

INFER_TYPE_SAMPLE_SIZE = 50


def convert_df_to_resp_obj(df: pd.DataFrame, column_type: str) -> dict:
    values = json.loads(df.to_json(orient="split", default_handler=str))
    values["data"] = flatten_json(values["data"])
    # values["data"] = values

    if len(df) > INFER_TYPE_SAMPLE_SIZE:
        df = df.sample(INFER_TYPE_SAMPLE_SIZE)

    columns = get_column_types(df, column_type)
    values["columns"] = columns
    return values


def flatten_json(json_data):
    data = []
    for row in json_data:
        new_row = []
        for value in row:
            new_row.append(value)
            # if isinstance(value, dict) or isinstance(value, list):
            #     new_row.append(json.dumps(value, default=str))
            # else:
            #     new_row.append(value)
        data.append(new_row)
    return data


def get_column_types(df, column_type: str):
    columns = []
    for col, dtype in df.dtypes.to_dict().items():
        col_type = str(dtype).lower()
        columns.append(
            {
                "name": col,
                "column_type": column_type,
                "data_type": str(dtype),
                "display_type": detect_col_type(col_type, df[col]),
            }
        )
    return columns


def detect_col_type(col_type: str, column: pd.Series):
    if "float" in col_type:
        return "float"
    elif "int" in col_type:
        return "integer"
    elif "date" in col_type:
        return "datetime"
    elif "bool" in col_type:
        return "boolean"
    if "object" in col_type:
        return infer_object_type(column)
    else:
        return "text"


def infer_object_type(column: pd.Series):
    if column.map(lambda x: type(x) is list).all():
        return "array"
    else:
        return "text"


# def get_column_types(df, column_type: str):
#     columns = []
#     for col, dtype in df.dtypes.to_dict().items():
#         col_type = str(dtype).lower()
#         columns.append(
#             {
#                 "name": col,
#                 "column_type": column_type,
#                 "data_type": str(dtype),
#                 "display_type": detect_col_type(col_type),
#             }
#         )
#     return columns


# def detect_col_type(col_type):
#     if "float" in col_type:
#         return "float"
#     elif "int" in col_type:
#         return "integer"
#     elif "date" in col_type:
#         return "datetime"
#     elif "bool" in col_type:
#         return "boolean"
#     else:
#         return "text"
