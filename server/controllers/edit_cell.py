from sqlalchemy import text

from server.schemas.edit_cell import CellEdit


def update_value(user_db_engine, edit: dict):
    edit = CellEdit(**edit)
    try:
        columns_name = edit.column_name
        column = edit.columns[columns_name]

        values = {
            "new_value": edit.new_value,
            "old_value": edit.old_value,
        }
        prim_key_list = []
        edit_keys = column.edit_keys
        for key in edit_keys:
            pk_col = edit.columns[key]
            prim_key_list.append(f"{pk_col.column_name} = :{pk_col.column_name}")
            values[pk_col.column_name] = edit.row[pk_col.name]
        prim_key_str = " AND ".join(prim_key_list)

        sql = f"""UPDATE "{column.schema_name}"."{column.table_name}"
    SET {column.column_name} = :new_value
    WHERE {prim_key_str}"""

        # TODO: add check for prev column value
        # AND {column.column_name} = :old_value

        with user_db_engine.connect() as conn:
            result = conn.execute(text(sql), values)
            conn.commit()
            if result.rowcount == 0:
                raise Exception("No rows were updated")
        return f"updated {edit.column_name} from {edit.old_value} to {edit.new_value}"
    except Exception as e:
        return f"Failed to update {edit.column_name} from {edit.old_value} to {edit.new_value}. Error: {str(e)}"  # noqa
