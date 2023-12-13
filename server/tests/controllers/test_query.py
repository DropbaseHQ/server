from server.schemas.table import TableFilter, TableSort


def test_query_db(mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.query.connect_to_user_db", return_value=mock_db)

    # from sqlalchemy import text
    from server.controllers.query import query_db

    # Act
    output = query_db("select * from users;", {}, "mock_source")

    # Assert
    assert len(output) > 0
    assert len(output[0]) > 0


def test_apply_filters():
    # Arrange
    from server.controllers.query import apply_filters

    table_sql = "select user_id, username, email from users"
    filters = [TableFilter(column_name="username", condition="=", value="Charlie Brown")]
    sorts = []

    # Act
    filter_sql, filter_values = apply_filters(table_sql, filters, sorts)

    # Assert

    filter = filters[0]
    assert (
        filter_sql
        == f'WITH user_query as ({table_sql}) SELECT * FROM user_query\nWHERE \nuser_query."{filter.column_name}" {filter.condition} :{filter.column_name}_filter\n\n'
    )
    assert filter_values == {f"{filter.column_name}_filter": "Charlie Brown"}


def test_apply_sorts():
    # Arrange
    from server.controllers.query import apply_filters

    table_sql = "select * from users"
    filters = []
    sorts = [TableSort(column_name="age", value="desc")]

    # Act
    filter_sql, _ = apply_filters(table_sql, filters, sorts)

    # Assert
    sort = sorts[0]
    assert (
        filter_sql
        == f'WITH user_query as ({table_sql}) SELECT * FROM user_query\n\nORDER BY \nuser_query."{sort.column_name}" {sort.value}\n'
    )


def test_get_table_columns_sql(mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.query.connect_to_user_db", return_value=mock_db)

    from server.controllers.query import get_table_columns

    # Act
    cols = get_table_columns(
        "dropbase_test_app",
        "page1",
        {"name": "test_sql", "type": "sql", "source": "mock_source"},
        {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    )

    # Assert
    assert set(cols) == {"user_id", "username", "email"}


def test_get_table_columns_python():
    # Arrange
    from server.controllers.query import get_table_columns

    # Act
    cols = get_table_columns(
        "dropbase_test_app",
        "page1",
        {"name": "test_function_data_fetcher", "type": "data_fetcher"},
        {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
    )

    # Assert
    assert set(cols) == {"x"}
