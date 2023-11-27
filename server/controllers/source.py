import functools

from sqlalchemy import inspect


@functools.lru_cache
def get_db_schema(user_db_engine):
    # TODO: cache this, takes a while
    inspector = inspect(user_db_engine)
    schemas = inspector.get_schema_names()
    default_search_path = inspector.default_schema_name

    db_schema = {}
    gpt_schema = {
        "metadata": {
            "default_schema": default_search_path,
        },
        "schema": {},
    }

    for schema in schemas:
        if schema == "information_schema":
            continue
        tables = inspector.get_table_names(schema=schema)
        gpt_schema["schema"][schema] = {}
        db_schema[schema] = {}

        for table_name in tables:
            columns = inspector.get_columns(table_name, schema=schema)

            # get primary keys
            primary_keys = inspector.get_pk_constraint(table_name, schema=schema)["constrained_columns"]

            # get foreign keys
            fk_constraints = inspector.get_foreign_keys(table_name, schema=schema)
            foreign_keys = []
            for fk_constraint in fk_constraints:
                foreign_keys.extend(fk_constraint["constrained_columns"])

            # get unique columns
            unique_constraints = inspector.get_unique_constraints(table_name, schema=schema)
            unique_columns = []
            for unique_constraint in unique_constraints:
                unique_columns.extend(unique_constraint["column_names"])

            db_schema[schema][table_name] = {}
            for column in columns:
                col_name = column["name"]
                is_pk = col_name in primary_keys
                db_schema[schema][table_name][col_name] = {
                    "schema_name": schema,
                    "table_name": table_name,
                    "column_name": col_name,
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "unique": col_name in unique_columns,
                    "primary_key": is_pk,
                    "foreign_key": col_name in foreign_keys,
                    "default": column["default"],
                    "edit_keys": primary_keys if not is_pk else [],
                }
            gpt_schema["schema"][schema][table_name] = [column["name"] for column in columns]
    return db_schema, gpt_schema
