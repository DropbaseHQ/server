from typing import Any, Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException
from server.constants import GPT_MODEL, GPT_TEMPERATURE
from . import gpt_templates as templates
import openai
import json


class ColumnInfo(BaseModel):
    schema_name: Optional[str]
    database_name: Optional[str]
    table_name: str
    column_name: str


class OutputSchema(BaseModel):
    output: Dict[str, ColumnInfo]


FullDBSchema = dict[str, dict[str, dict[str, dict[str, Any]]]]


def get_gpt_input(
    db_schema: dict, user_sql: str, column_names: list, db_type: str
) -> str:
    match db_type:
        case "postgres":
            return templates.get_postgres_gpt_input(db_schema, user_sql, column_names)
        case "mysql":
            return templates.get_mysql_gpt_input(db_schema, user_sql, column_names)
        case "snowflake":
            return templates.get_snowflake_gpt_input(db_schema, user_sql, column_names)
        case "sqlite":
            return templates.get_sqlite_gpt_input(db_schema, user_sql, column_names)
        case _:
            return templates.get_postgres_gpt_input(db_schema, user_sql, column_names)


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

        raise HTTPException(
            status_code=500, detail="API call failed. Please try again."
        )
