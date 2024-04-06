import copy
import time

import pytest

from server.tests.verify_property_exists import verify_property_exists

base_table_data = {
    "app_name": "dropbase_test_app",
    "page_name": "page1",
    "properties": {
        "blocks": [
            {
                "block_type": "table",
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
            },
            {
                "block_type": "table",
                "label": "Table3",
                "name": "table3",
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
            },
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
    "state": {"tables": {"table2": {}, "table3": {}}, "widgets": {}},
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
        "SELECT * FROM orders;",
        "SELECT * FROM orders order by order_id",
        "SELECT order_id FROM orders INNER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id FROM orders FULL OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id FROM orders LEFT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id FROM orders RIGHT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT * FROM orders WHERE order_id = 1",
        "SELECT order_id AS id FROM orders",
        "SELECT * from ORDERS WHERE product_name LIKE '%Mouse%'",
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

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")

    # Assertions
    assert job_status.status_code == 200
    res_data["message"] == "job started"
    assert verify_property_exists("tables[0].smart", True)


@pytest.mark.parametrize("mock_db", ["mysql"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * FROM orders",
        "SELECT * FROM orders;",
        "SELECT * FROM orders order by order_id",
        "SELECT order_id From orders INNER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id From orders LEFT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT order_id From orders RIGHT OUTER JOIN users ON orders.order_id=users.user_id",
        "SELECT * FROM orders WHERE order_id = 1",
        "SELECT order_id AS id FROM orders",
        "SELECT * from ORDERS WHERE product_name LIKE '%Mouse%'",
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

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")

    # Assertions
    assert job_status.status_code == 200
    res_data["message"] == "job started"
    assert verify_property_exists("tables[0].smart", True)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * From orders INNER JOIN users ON orders.order_id=users.user_id",
    ],
    indirect=True,
)
def test_convert_to_smart_table_duplicate_column_name_fail(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")
    status_data = job_status.json()

    # Assertions
    assert "Duplicate column name" in status_data["message"]
    assert status_data["type"] == "error"
    assert verify_property_exists("tables[0].smart", False)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT product_name FROM orders GROUP BY product_name",
    ],
    indirect=True,
)
def test_convert_to_smart_table_banned_keyword_groupby_fail(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")
    status_data = job_status.json()

    # Assertions
    assert "Must remove keyword GROUP BY to convert to smart table" in status_data["message"]
    assert status_data["type"] == "error"
    assert verify_property_exists("tables[0].smart", False)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "WITH simple_table AS (select order_id, product_name FROM orders) SELECT * FROM simple_table",
    ],
    indirect=True,
)
def test_convert_to_smart_table_banned_keyword_with_fail(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")
    status_data = job_status.json()

    # Assertions
    assert "Must remove keyword WITH to convert to smart table" in status_data["message"]
    assert status_data["type"] == "error"
    assert verify_property_exists("tables[0].smart", False)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    ["SELECT * FROM NoPrimaryKey", "SELECT * FROM NoPrimaryKey WHERE quantity > 1"],
    indirect=True,
)
def test_convert_to_smart_table_no_pk(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")

    # Assertions
    assert job_status.status_code == 200
    res_data["message"] == "job started"
    assert verify_property_exists("tables[0].smart", True)
    assert verify_property_exists("tables[0].columns[1].editable", False)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * FROM orders WHERE product_name LIKE '%with%'",
    ],
    indirect=True,
)
def test_convert_to_smart_table_empty_table_fail(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")
    status_data = job_status.json()

    # Assertions
    assert "Can not convert empty table into smart table" in status_data["message"]
    assert status_data["type"] == "error"
    assert verify_property_exists("tables[0].smart", False)


@pytest.mark.parametrize("mock_db", ["postgres", "mysql", "snowflake", "sqlite"], indirect=True)
@pytest.mark.parametrize(
    "setup_tables",
    [
        "SELECT * FROM orders",
    ],
    indirect=True,
)
def test_convert_to_smart_table_in_parallel(test_client, mocker, mock_db, setup_tables):
    # Arrange
    smart_data = copy.deepcopy(base_smart_table_data)

    headers = {"access-token": "mock access token"}
    mocker.patch("server.controllers.tables.connect", return_value=mock_db)

    # Act
    res = test_client.post("/tables/convert", json=smart_data, headers=headers)
    res_data = res.json()

    job_id = res_data["job_id"]
    job_status = test_client.get(f"/status/{job_id}")

    time.sleep(3)

    smart_data_2 = copy.deepcopy(base_smart_table_data)
    smart_data_2["table"]["label"] = "Table3"
    smart_data_2["table"]["name"] = "table3"

    res_2 = test_client.post("/tables/convert", json=smart_data_2, headers=headers)
    res_data_2 = res_2.json()

    job_id_2 = res_data_2["job_id"]
    job_status_2 = test_client.get(f"/status/{job_id_2}")

    # Assertions
    assert job_status.status_code == 200
    assert res_data["message"] == "job started"
    assert verify_property_exists("tables[0].smart", True)
    assert job_status_2.status_code == 200
    assert res_data_2["message"] == "job started"
    assert verify_property_exists("tables[1].smart", True)
