import datetime
import json

import pandas as pd

from dropbase.constants import INFER_TYPE_SAMPLE_SIZE


def to_dtable(self, data_type: str = "python"):
    # dropbase_data_type is a metadata we add to the dataframe to keep track of the source type
    # for example if it's originated from querying sqlite, it will be "sqlite"
    if "dropbase_data_type" in self.__dict__:
        data_type = self.dropbase_data_type

    values = json.loads(self.to_json(orient="split", default_handler=str))

    # sample down
    if len(self) > INFER_TYPE_SAMPLE_SIZE:
        self = self.sample(INFER_TYPE_SAMPLE_SIZE)

    # infer column types
    columns = get_column_types(self, column_type=data_type)
    values["columns"] = columns
    values["type"] = data_type
    return values


def get_column_types(df: pd.DataFrame, column_type: str = "python"):
    columns = []
    for col, dtype in df.dtypes.items():
        data_type = str(dtype).lower()
        columns.append(
            {
                "name": col,
                "data_type": data_type,
                "display_type": detect_col_type(data_type, df[col]),
                "column_type": column_type,
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
