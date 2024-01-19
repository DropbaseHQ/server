import shutil
import tempfile

import psycopg2
import pytest
import pytest_postgresql.factories
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from server.controllers.properties import read_page_properties, update_properties
from server.main import app
from server.requests.dropbase_router import get_dropbase_router
from server.tests.constants import (
    DEMO_INIT_SQL_PATH,
    TEMPDIR_PATH,
    TEST_APP_NAME,
    TEST_PAGE_NAME,
    WORKSPACE_PATH,
)
from server.tests.mocks.dropbase_router_mocker import DropbaseRouterMocker


# Setup pytest-postgresql db with test data
def load_test_db(**kwargs):
    conn = psycopg2.connect(**kwargs)
    with open(DEMO_INIT_SQL_PATH, "r") as rf:
        init_sql = rf.read()
    with conn.cursor() as cur:
        cur.execute(init_sql)
        conn.commit()


postgresql_proc = pytest_postgresql.factories.postgresql_proc(load=[load_test_db])
postgresql = pytest_postgresql.factories.postgresql("postgresql_proc")


@pytest.fixture(autouse=True)
def test_workspace():
    # used by all tests, so autouse=True
    with tempfile.TemporaryDirectory() as workspace_backup_path:
        # backup workspace
        shutil.copytree(WORKSPACE_PATH, workspace_backup_path, dirs_exist_ok=True)
        yield
        # delete workspace modified by test
        shutil.rmtree(WORKSPACE_PATH)
        # restore backup
        shutil.copytree(workspace_backup_path, WORKSPACE_PATH)


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture
def dropbase_router_mocker():
    mocker = DropbaseRouterMocker()
    # app.dependency_overrides uses function as a key. part of fastapi
    app.dependency_overrides[get_dropbase_router] = lambda: mocker.get_mock_dropbase_router()
    yield mocker
    # delete get_dropbase_router from dependency overwrite once test is done
    del app.dependency_overrides[get_dropbase_router]


@pytest.fixture
def mock_db(postgresql):
    connection = f"postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"
    return create_engine(connection, echo=False, poolclass=NullPool)


def pytest_sessionstart():

    import unittest.mock

    from server.controllers.workspace import AppCreator, create_file, create_folder
    from server.tests.mocks.dropbase.app import update_app_response
    from server.tests.mocks.dropbase.sync import sync_components_response_empty

    create_folder(TEMPDIR_PATH)

    mock_dropbase_router = unittest.mock.MagicMock()
    mock_dropbase_router.misc.sync_components.side_effect = sync_components_response_empty
    mock_dropbase_router.app.update_app.side_effect = update_app_response

    AppCreator(
        TEST_APP_NAME,
        WORKSPACE_PATH,
    ).create()

    scripts_path = WORKSPACE_PATH.joinpath(f"{TEST_APP_NAME}/{TEST_PAGE_NAME}/scripts")
    create_file(scripts_path, "", "function1.py")
    create_file(
        scripts_path,
        f'from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context\ndef test_ui(state: State, context: Context) -> Context:\n\n\n    print("test")\n    return context\n',
        "test_ui.py",
    )
    create_file(
        scripts_path,
        f'import pandas as pd\nfrom workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context\ndef test_data_fetcher(state: State) -> pd.DataFrame:\n\n    return pd.DataFrame(data=[[1]], columns=["x"])\n',
        "test_data_fetcher.py",
    )
    create_file(scripts_path, "select * from users;", "test_sql.sql")

    # add files to properties
    properties = read_page_properties(TEST_APP_NAME, TEST_PAGE_NAME)
    properties["files"] = [
        {"name": "test_sql", "type": "sql", "source": "local", "depends_on": []},
        {"name": "test_ui", "type": "ui", "source": None, "depends_on": None},
        {"name": "test_data_fetcher", "type": "data_fetcher", "source": None, "depends_on": None},
    ]
    update_properties(TEST_APP_NAME, TEST_PAGE_NAME, properties)


def pytest_sessionfinish():
    import shutil

    shutil.rmtree(WORKSPACE_PATH.joinpath("dropbase_test_app"))
