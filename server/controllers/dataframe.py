import json
from datetime import date, time

import numpy as np
import pandas as pd

from server.constants import INFER_TYPE_SAMPLE_SIZE


def convert_df_types(df):
    for col in df.columns:
        # Check if column is of object type
        if df[col].dtype == "object":
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].isnull().all():
                df[col] = df[col].astype(str)
        # Check if column is of boolean type
        elif df[col].dtype == np.bool_:
            continue
        # Check if column is of integer type
        elif pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype(int)
        # Check if column is of datetime type
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            if df[col].apply(lambda x: isinstance(x, date)).all():
                df[col] = df[col].astype(date)
            elif df[col].apply(lambda x: isinstance(x, time)).all():
                df[col] = df[col].astype(time)
        # Check if column is of float type
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype(float)
        # If column is of none of the above types, convert it to string
        else:
            df[col] = df[col].astype(str)
    return df


column_type_mapper = {
    "int64": "integer",
    "float64": "float",
    "object": "text",
    "bool": "boolean",
    "datetime64[ns]": "datetime",
    "date": "date",  # TODO: to implement
    "time": "time",  # TODO: to implement
}


def get_column_types(df):
    df = convert_df_types(df)
    return {col: column_type_mapper[str(dtype)] for col, dtype in df.dtypes.to_dict().items()}


def convert_df_to_resp_obj(df: pd.DataFrame) -> dict:
    values = json.loads(df.to_json(orient="split", default_handler=str))
    values["data"] = flatten_json(values["data"])
    # TODO: return column types only for columns that are not present in table data
    if len(df) > INFER_TYPE_SAMPLE_SIZE:
        df = df.sample(INFER_TYPE_SAMPLE_SIZE).copy()
    column_types = get_column_types(df)
    values["types"] = column_types
    return values


def flatten_json(json_data):
    data = []
    for row in json_data:
        new_row = []
        for value in row:
            if isinstance(value, dict) or isinstance(value, list):
                new_row.append(json.dumps(value, default=str))
            else:
                new_row.append(value)
        data.append(new_row)
    return data
