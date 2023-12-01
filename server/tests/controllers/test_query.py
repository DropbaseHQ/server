import unittest.mock

from server.schemas.table import TableFilter, TableSort


def test_query_db(mocker):
    # Arrange
    mock_db = unittest.mock.MagicMock()
    mocker.patch("server.controllers.query.connect_to_user_db", return_value=mock_db)

    from sqlalchemy import text
    from server.controllers.query_old import query_db

    # Act
    output = query_db("select 1;", {}, "mock source")

    # Assert
    call_args_sql, call_args_values = mock_db.connect().execution_options().__enter__().execute.call_args.args
    assert str(call_args_sql) == "select 1;"
    assert call_args_values == {}
    mock_db.dispose.assert_called_once()


def test_apply_filters(mocker):
    # Arrange
    from server.controllers.query_old import apply_filters

    table_sql = "select id, name, age from users where name='johncena'"
    filters = [TableFilter(column_name="age", condition=">", value=67)]
    sorts = []

    # Act
    filter_sql, filter_values = apply_filters(table_sql, filters, sorts)

    # Assert
    filter = filters[0]
    assert filter_sql == f"WITH user_query as ({table_sql}) SELECT * FROM user_query\nWHERE \nuser_query.\"{filter.column_name}\" {filter.condition} :age_filter\n\n"
    assert filter_values == {"age_filter": 67}


def test_apply_sorts(mocker):
    # Arrange
    from server.controllers.query_old import apply_filters

    table_sql = "select * from users where name='johncena'"
    filters = []
    sorts = [TableSort(column_name="age", value="desc")]

    # Act
    filter_sql, filter_values = apply_filters(table_sql, filters, sorts)

    # Assert
    sort = sorts[0]
    assert filter_sql == f"WITH user_query as ({table_sql}) SELECT * FROM user_query\n\nORDER BY \nuser_query.\"{sort.column_name}\" {sort.value}\n"
