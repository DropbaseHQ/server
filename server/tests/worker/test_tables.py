import unittest.mock

from sqlalchemy import INTEGER, VARCHAR

from server.tests.mocks.dropbase.misc import get_smart_columns_response, update_smart_columns_response


def test_convert_sql_table(test_client, mocker):
    # Arrange
    mock_router = unittest.mock.MagicMock()
    mock_router.misc.get_smart_columns.side_effect = get_smart_columns_response
    mock_router.misc.update_smart_columns.side_effect = update_smart_columns_response
    mocker.patch("server.worker.tables.DropbaseRouter", return_value=mock_router)

    mock_db = unittest.mock.MagicMock()
    mocker.patch("server.worker.tables.connect_to_user_db", return_value=mock_db)

    mock_inspector = unittest.mock.MagicMock()
    mock_inspector.default_schema_name = "public"
    mock_inspector.get_schema_names.return_value = ["information_schema", "public"]
    mock_inspector.get_table_names.return_value = ["users"]
    mock_inspector.get_columns.return_value = [
        {
            "name": "id",
            "type": VARCHAR(),
            "nullable": False,
            "default": None,
            "autoincrement": False,
            "comment": None,
        },
        {
            "name": "name",
            "type": VARCHAR(),
            "nullable": True,
            "default": None,
            "autoincrement": False,
            "comment": None,
        },
        {
            "name": "age",
            "type": INTEGER(),
            "nullable": True,
            "default": None,
            "autoincrement": False,
            "comment": None,
        },
    ]
    mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
    mock_inspector.get_foreign_keys.return_value = []
    mock_inspector.get_unique_constraints.return_value = []
    mocker.patch("server.controllers.source.inspect", return_value=mock_inspector)

    from server.controllers.tables import convert_sql_table

    # Act
    output = convert_sql_table(
        app_name="dropbase_test_app",
        page_name="page1",
        table={
            "name": "table1",
            "property": {
                "filters": [],
                "appears_after": None,
                "on_row_change": None,
                "on_row_selection": None,
            },
            "page_id": "8f1dabeb-907b-4e59-8417-ba67a801ba0e",
        },
        file={"name": "test_sql", "type": "sql", "source": "replica"},
        state={"widgets": {"widget1": {}}, "tables": {"table1": {}}},
        access_cookies=None,
    )

    # Assert
    assert output["message"] == "success"
