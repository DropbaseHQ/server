from server.schemas.table import TableFilter, TableSort


def test_query_db(mocker, mock_db):
    # Arrange
    mocker.patch("server.controllers.connect.connect_to_user_db", return_value=mock_db)

    # Act
    output = mock_db._run_query("select * from users;", {})

    # Assert
    # TODO: improve assertions
    assert len(output) > 0
    assert len(output[0]) > 0


def test_apply_filters():
    # Arrange
    from server.controllers.run_sql import apply_filters

    table_sql = "select user_id, username, email from users"
    filters = [TableFilter(column_name="username", condition="=", value="Charlie Brown")]
    sorts = []

    # Act
    filter_sql, filter_values = apply_filters(table_sql, filters, sorts)

    # Assert

    filter = filters[0]
    assert (
        filter_sql
        == f'WITH user_query as ({table_sql}) SELECT * FROM user_query\nWHERE \nuser_query."{filter.column_name}" {filter.condition} :{filter.column_name}_filter\n\n'  # noqa
    )
    assert filter_values == {f"{filter.column_name}_filter": "Charlie Brown"}


def test_apply_sorts():
    # Arrange
    from server.controllers.run_sql import apply_filters

    table_sql = "select * from users"
    filters = []
    sorts = [TableSort(column_name="age", value="desc")]

    # Act
    filter_sql, _ = apply_filters(table_sql, filters, sorts)

    # Assert
    sort = sorts[0]
    assert (
        filter_sql
        == f'WITH user_query as ({table_sql}) SELECT * FROM user_query\n\nORDER BY \nuser_query."{sort.column_name}" {sort.value}\n'  # noqa
    )
