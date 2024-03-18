import datetime
import json

import pandas as pd

from dropbase.constants import INFER_TYPE_SAMPLE_SIZE


def convert_df_to_resp_obj(df: pd.DataFrame, column_type: str) -> dict:
    values = json.loads(df.to_json(orient="split", default_handler=str))

    if len(df) > INFER_TYPE_SAMPLE_SIZE:
        df = df.sample(INFER_TYPE_SAMPLE_SIZE)

    columns = get_column_types(df, column_type)
    values["columns"] = columns
    return values


def get_column_types(df, column_type: str):
    columns = []
    for col, dtype in df.dtypes.items():
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
    type_names = ["array", "datetime", "date", "time", "text"]
    types = [0, 0, 0, 0, 0]
    for col in column:
        inferred_type = type(col)
        if inferred_type is list:
            types[0] += 1
        elif inferred_type is datetime.datetime:
            types[1] += 1
        elif inferred_type is datetime.date:
            types[2] += 1
        elif inferred_type is datetime.time:
            types[3] += 1
        else:
            types[4] += 1
    type_index = types.index(max(types))
    return type_names[type_index]
