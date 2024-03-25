import shutil
import tempfile

import pytest
import pytest_postgresql.factories
from fastapi.testclient import TestClient

# from pytest_mysql import factories

from server.auth.dependency import CheckUserPermissions
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.workspace import WorkspaceFolderController
from server.main import app
from server.requests.dropbase_router import WSDropbaseRouterGetter, get_dropbase_router
from server.tests.constants import (
    MYSQL_TEST_CONNECTION_PARAMS,
    MYSQL_TEST_CREDS,
    SNOWFLAKE_TEST_CONNECTION_PARAMS,
    SNOWFLAKE_TEST_CREDS,
    SQLITE_TEST_CONNECTION_PARAMS,
    SQLITE_TEST_CREDS,
    TEMPDIR_PATH,
    TEST_APP_NAME,
    TEST_PAGE_NAME,
    WORKSPACE_PATH,
)
from server.tests.databases import (
    snowflake_db,
    sqlite_db,
)  # noqa NOTE: used by mock_db, do not remove
from server.tests.mocks.dropbase_router_mocker import DropbaseRouterMocker
from server.tests.templates import get_test_data_fetcher, get_test_ui
from server.tests.utils import connect_to_test_db, load_test_db

postgresql_proc = pytest_postgresql.factories.postgresql_proc(load=[load_test_db])
postgres_db = pytest_postgresql.factories.postgresql("postgresql_proc")

# mysql_proc = factories.mysql_proc(port=3307)
# mysql_db = factories.mysql("mysql_proc")


@pytest.fixture(scope="module", autouse=True)
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
    def override_check_user_app_permissions():
        return {"use": True, "edit": True, "own": True}

    app.dependency_overrides[CheckUserPermissions(action="edit")] = (
        override_check_user_app_permissions
    )
    app.dependency_overrides[CheckUserPermissions(action="use")] = (
        override_check_user_app_permissions
    )
    app.dependency_overrides[
        CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP)
    ] = override_check_user_app_permissions
    app.dependency_overrides[
        CheckUserPermissions(action="use", resource=CheckUserPermissions.APP)
    ] = override_check_user_app_permissions
    app.dependency_overrides[
        CheckUserPermissions(action="edit", resource=CheckUserPermissions.WORKSPACE)
    ] = override_check_user_app_permissions
    app.dependency_overrides[
        CheckUserPermissions(action="use", resource=CheckUserPermissions.WORKSPACE)
    ] = override_check_user_app_permissions
    return TestClient(app)


@pytest.fixture
def dropbase_router_mocker():
    mocker = DropbaseRouterMocker()
    # app.dependency_overrides uses function as a key. part of fastapi
    app.dependency_overrides[get_dropbase_router] = (
        lambda: mocker.get_mock_dropbase_router()
    )
    app.dependency_overrides[WSDropbaseRouterGetter(access_token="temp")] = (
        lambda: mocker.get_mock_dropbase_router()
    )
    yield mocker
    # delete get_dropbase_router from dependency overwrite once test is done
    del app.dependency_overrides[get_dropbase_router]


@pytest.fixture
def mock_db(request, postgres_db, mysql_db, snowflake_db, sqlite_db):  # noqa
    # returns a database instance rather than an engine
    db_type = request.param
    creds_dict = {}
    match db_type:
        case "postgres":
            creds_dict = {
                "host": postgres_db.info.host,
                "drivername": "postgresql+psycopg2",
                "database": postgres_db.info.dbname,
                "username": postgres_db.info.user,
                "password": "",  # Not required for pytest-postgresql
                "port": postgres_db.info.port,
            }

            db_instance = connect_to_test_db("postgres", creds_dict)

        case "mysql":
            load_test_db("mysql", **MYSQL_TEST_CONNECTION_PARAMS)
            db_instance = connect_to_test_db("mysql", MYSQL_TEST_CREDS)

        case "snowflake":
            load_test_db("snowflake", **SNOWFLAKE_TEST_CONNECTION_PARAMS)
            db_instance = connect_to_test_db("snowflake", SNOWFLAKE_TEST_CREDS)

        case "sqlite":
            load_test_db("sqlite", **SQLITE_TEST_CONNECTION_PARAMS)
            db_instance = connect_to_test_db("sqlite", SQLITE_TEST_CREDS)

    return db_instance


def pytest_sessionstart():
    from server.controllers.workspace import (
        AppFolderController,
        create_file,
        create_folder,
    )

    create_folder(TEMPDIR_PATH)

    AppFolderController(
        TEST_APP_NAME,
        WORKSPACE_PATH,
    ).create_app()

    scripts_path = WORKSPACE_PATH.joinpath(f"{TEST_APP_NAME}/{TEST_PAGE_NAME}/scripts")
    create_file(scripts_path, "", "function1.py")
    create_file(scripts_path, get_test_ui(), "test_ui.py")
    create_file(scripts_path, get_test_data_fetcher(), "test_data_fetcher.py")
    create_file(scripts_path, "select * from users;", "test_sql.sql")

    # add files to properties
    properties = read_page_properties(TEST_APP_NAME, TEST_PAGE_NAME)
    properties["files"] = [
        {"name": "test_sql", "type": "sql", "source": "local", "depends_on": []},
        {"name": "test_ui", "type": "ui", "source": None, "depends_on": None},
        {
            "name": "test_data_fetcher",
            "type": "data_fetcher",
            "source": None,
            "depends_on": None,
        },
    ]
    update_properties(TEST_APP_NAME, TEST_PAGE_NAME, properties)


def pytest_sessionfinish():
    import shutil

    shutil.rmtree(WORKSPACE_PATH.joinpath("dropbase_test_app"))
    # Workspace properties is still written to the non test workspace
    # Its easier to clean it up here
    workspace_folder_controller = WorkspaceFolderController(
        r_path_to_workspace=WORKSPACE_PATH
    )
    workspace_props = workspace_folder_controller.get_workspace_properties()
    workspace_apps = workspace_props.get("apps", [])
    for one_app in workspace_apps:
        if one_app["name"] == TEST_APP_NAME:
            workspace_apps.remove(one_app)

    workspace_folder_controller.write_workspace_properties(
        {**workspace_props, "apps": workspace_apps}
    )
