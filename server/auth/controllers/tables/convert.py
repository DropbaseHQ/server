import json
from typing import Any, Dict, Union
from fastapi import HTTPException
import logging

import openai
from typing import Optional
from pydantic import BaseModel

from server.constants import GPT_MODEL, GPT_TEMPERATURE
from ...controllers.tables.pg_column import SqlSmartColumnProperty
from server.credentials import OPENAI_API_KEY, OPENAI_ORG_ID

from .gpt_template import get_gpt_input

openai.organization = OPENAI_ORG_ID
openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(__name__)


class ColumnInfo(BaseModel):
    schema_name: Optional[str]
    database_name: Optional[str]
    table_name: str
    column_name: str


class OutputSchema(BaseModel):
    output: Dict[str, ColumnInfo]


FullDBSchema = dict[str, dict[str, dict[str, dict[str, Any]]]]


def fill_smart_cols_data(
    smart_col_paths: dict, db_schema: FullDBSchema
) -> dict[str, Union[SqlSmartColumnProperty]]:
    # If we want to add more
    try:
        smart_cols_data = {}
        for name, col_path in smart_col_paths.items():
            try:
                table = col_path["table_name"]
                column = col_path["column_name"]
                if "schema_name" in col_path:
                    schema = col_path["schema_name"]
                    col_schema_data = db_schema[schema][table][column]
                elif (
                    "database_name" in col_path
                ):  # Mysql and Sqlite don't have a schema, instead we take its database
                    database = col_path["database_name"]
                    table = col_path["table_name"]
                    col_schema_data = db_schema[database][table][column]
            except KeyError:
                # Skip ChatGPT "hallucinated" columns
                continue
            smart_cols_data[name] = SqlSmartColumnProperty(name=name, **col_schema_data)
        return {"columns": smart_cols_data}
    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=500, detail="API call failed. Please try again."
        )


def call_gpt(
    user_sql: str, column_names: list, db_schema: dict, db_type: str
) -> OutputSchema:
    try:
        gpt_input = get_gpt_input(db_schema, user_sql, column_names, db_type)
        gpt_output = str(
            openai.ChatCompletion.create(
                model=GPT_MODEL,
                temperature=GPT_TEMPERATURE,
                messages=[{"role": "user", "content": gpt_input}],
            )
        )

        output_dict = json.loads(gpt_output).get(
            "choices", [{"message": {"content": "{}"}}]
        )[0]["message"]["content"]

        output = json.loads(output_dict)
        # validate output
        OutputSchema(output=output)
        return output
    except Exception as e:
        logger.info(str(e))
        raise HTTPException(
            status_code=500, detail="API call failed. Please try again."
        )