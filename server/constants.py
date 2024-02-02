import os
import re

cwd = os.getcwd()


DROPBASE_TOKEN = os.getenv("DROPBASE_TOKEN")
DROPBASE_API_URL = (
    os.getenv("DROPBASE_API_URL") if os.getenv("DROPBASE_API_URL") else "https://api.dropbase.io"
)
TASK_TIMEOUT = os.getenv("TASK_TIMEOUT") if os.getenv("TASK_TIMEOUT") else 60
DATA_PREVIEW_SIZE = 100
INFER_TYPE_SAMPLE_SIZE = 50

FILE_NAME_REGEX = re.compile(r"^[A-Za-z0-9_.]+$")
WORKER_VERSION = "0.2.0"

pg_base_type_mapper = {
    "TEXT": "text",
    "VARCHAR": "text",
    "CHAR": "text",
    "CHARACTER": "text",
    "STRING": "text",
    "BINARY": "text",
    "VARBINARY": "text",
    "INTEGER": "integer",
    "INT": "integer",
    "BIGINT": "integer",
    "SMALLINT": "integer",
    "TINYINT": "integer",
    "BYTEINT": "integer",
    "REAL": "float",
    "FLOAT": "float",
    "FLOAT4": "float",
    "FLOAT8": "float",
    "DOUBLE": "float",
    "DOUBLE PRECISION": "float",
    "DECIMAL": "float",
    "NUMERIC": "float",
    "BOOLEAN": "boolean",
    "DATE": "date",
    "TIME": "time",
    "DATETIME": "datetime",
    "TIMESTAMP": "datetime",
    "TIMESTAMP_LTZ": "datetime",
    "TIMESTAMP_NTZ": "datetime",
    "TIMESTAMP_TZ": "datetime",
    "VARIANT": "text",
    "OBJECT": "text",
    "ARRAY": "text",
}
