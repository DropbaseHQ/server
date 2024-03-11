import copy

import pytest

from server.tests.verify_property_exists import verify_property_exists

base_table_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "tables": [
            {
                "label": "Table2",
                "name": "table2",
                "description": None,
                "fetcher": "function3",
                "height": "",
                "size": 10,
                "filters": None,
                "type": "sql",
                "smart": False,
                "columns": [
                    {
                        "name": "customer_id",
                        "column_type": "postgres",
                        "data_type": "int64",
                        "display_type": "integer",
                    },
                    {
                        "name": "company_name",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "contact_name",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "phone_number",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                    {
                        "name": "customer_type",
                        "column_type": "postgres",
                        "data_type": "object",
                        "display_type": "text",
                    },
                ],
            }
        ],
        "widgets": [],
        "files": [{"name": "function3", "type": "sql", "source": "dropbasedev", "depends_on": []}],
    },
}

base_smart_table_data = {
    "table": {
        "label": "Table2",
        "name": "table2",
        "description": None,
        "fetcher": "function3",
        "height": "",
        "size": 10,
        "filters": None,
        "type": "sql",
        "smart": False,
        "columns": [],
    },
    "state": {"tables": {"table1": {}, "table2": {}}, "widgets": {}},
    "app_name": "dropbase_test_app",
    "page_name": "page1",
}

base_file_data = {
    "name": "function3",
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "type": "sql",
    "source": "dropbasedev",
}

base_add_file_data = {
    "page_name": "page1",
    "app_name": "dropbase_test_app",
    "file_name": "function3",
    "code": "SELECT * FROM users",
    "source": "dropbasedev",
    "type": "sql",
}


@pytest.fixture(scope="session")
def setup_tables(request, test_client):
    # Arrange
    table_data = copy.deepcopy(base_table_data)
    file_data = copy.deepcopy(base_file_data)
    add_file_data = copy.deepcopy(base_add_file_data)

    source_code = request.param
    add_file_data["code"] = f"{source_code}"

    headers = {"access-token": "mock access token"}

    test_client.post("/files/", json=file_data)
    test_client.put("/files/function3", json=add_file_data)
    test_client.put("/page", json=table_data, headers=headers)


@pytest.mark.parametrize("mock_db", ["postgres", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * FROM orders",
        "SELECT * FROM orders order by order_id",
        "SELECT order_id from orders INNER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id from orders FULL OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id from orders LEFT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id from orders RIGHT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT * FROM orders WHERE order_id = 1",  # "SELECT order_id AS id FROM orders" ADD THIS CASE
    ],
    indirect=True,
)
def test_convert_to_smart_table(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    # Assertions
    assert res_data["state"]["tables"]["table2"]
    assert verify_property_exists("tables[0].smart", True)


@pytest.mark.parametrize("mock_db", ["mysql"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * FROM orders",
        "SELECT * FROM orders order by order_id",
        "SELECT order_id from orders INNER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id from orders LEFT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id from orders RIGHT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT * FROM orders WHERE order_id = 1",  # "SELECT order_id AS id FROM orders" ADD THIS CASE
    ],
    indirect=True,
)
def test_convert_to_smart_table_mysql(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    # Assertions
    assert res_data["state"]["tables"]["table2"]
    assert verify_property_exists("tables[0].smart", True)
