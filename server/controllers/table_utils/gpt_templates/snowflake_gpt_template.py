def get_snowflake_gpt_input(db_schema: dict, user_sql: str, column_names: list) -> str:
    return f"""Given a database schema and a SQL query, output a JSON object that contains each column referenced in the SQL query.

Sample JSON object key
```json
"output column"
```

Sample JSON object value
```json
{{
        "name": "output column",
        "schema_name": "public",
        "table_name": "customer",
        "column_name": "name"
}}
```
This is only a sample value, only name the schema_name "public" if it is actually public. 
This part is extremely important please be careful. When trying to find the "schema_name" ENSURE that the schema_name consists of the table that is queried in user_query.
Loop through all the schema_names under the values under the "schema" key until you find a key (under the schema key) that is titled the same as the table in the query, when you find it assign that schema to be the schema_name
If you absolutely can not find a match then use the "default_schema" under the "meta_data" key. Be sure to check the, the default_schema is not always the right schema.

In the sample JSON, "output column" is the column name as it would be output when executing the SQL statement.
You will be provided a list of column names that will be returned by the query. Your job is to, for each column name, determine its schema_name, table_name, and column_name based on the SQL query. You may only return information on the columns specified in Column names. You must return information on each of the columns specified in Column names.
"table" is the table name and "column" is the column name, both are inferred from the SQL query.
"schema" is the schema, this can be found by referencing the Database schema.

Make sure you include each and every column referenced in the SQL statement. Do not miss any columns. When in doubt, make a guess about which column is part of which table based on your understanding of the world and web application building to make sure all columns are covered.

Database schema
```json
{db_schema}
```

SQL query:
```sql
{user_sql}
```

Column names:
```json
{column_names}
```

Output no prose, no explanations, just JSON. Exclude calculated columns from the JSON output. Don't format output. Ensure that the output is one JSON object not multiple. Furthermore label the output column the actual column name don't just call it "output column". 
"""  # noqa
