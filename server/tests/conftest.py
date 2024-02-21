import shutil
import sqlite3
import tempfile

import psycopg2
import pytest
import pytest_postgresql.factories
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dropbase.database.databases.postgres import PostgresDatabase
from dropbase.database.databases.sqlite import SqliteDatabase
from server.auth.dependency import CheckUserPermissions
from server.controllers.properties import read_page_properties, update_properties
from server.controllers.workspace import WorkspaceFolderController
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
from server.tests.templates import get_test_data_fetcher, get_test_ui


# Setup pytest-postgresql db with test data
def load_test_db(db_type="postgres", **kwargs):
    if db_type == "postgres":
        conn = psycopg2.connect(**kwargs)
    elif db_type == "sqlite":
        conn = sqlite3.connect(**kwargs)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

    if db_type == "postgres":
        with open(DEMO_INIT_SQL_PATH, "r") as rf:
            init_sql = rf.read()
    elif db_type == "snowflake":
        with open(DEMO_INIT_SQL_PATH, "r") as rf:  # Replace this with snowflake path
            init_sql = rf.read()

    with conn.cursor() as cur:
        cur.execute(init_sql)
        if db_type == "sqlite":
            # Sqlite might require splitting and executing each statement separately
            for statement in init_sql.split(";"):
                if statement.strip():
                    cur.execute(statement)
        else:
            cur.execute(init_sql)
        conn.commit()


@pytest.fixture
def sqlite_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)

    return TestSession()


postgresql_proc = pytest_postgresql.factories.postgresql_proc(load=[load_test_db])
postgresql = pytest_postgresql.factories.postgresql("postgresql_proc")


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

    app.dependency_overrides[CheckUserPermissions(action="edit")] = override_check_user_app_permissions
    app.dependency_overrides[CheckUserPermissions(action="use")] = override_check_user_app_permissions
    app.dependency_overrides[
        CheckUserPermissions(action="edit", resource=CheckUserPermissions.APP)
    ] = override_check_user_app_permissions
    app.dependency_overrides[
        CheckUserPermissions(action="use", resource=CheckUserPermissions.APP)
    ] = override_check_user_app_permissions
    return TestClient(app)


@pytest.fixture
def dropbase_router_mocker():
    mocker = DropbaseRouterMocker()
    # app.dependency_overrides uses function as a key. part of fastapi
    app.dependency_overrides[get_dropbase_router] = lambda: mocker.get_mock_dropbase_router()
    yield mocker
    # delete get_dropbase_router from dependency overwrite once test is done
    del app.dependency_overrides[get_dropbase_router]


def connect_to_test_db(db_type: str, creds: dict):
    # utility function to assist in creating the db instance
    match db_type:
        case "postgres":
            return PostgresDatabase(creds)
        case "pg":
            return PostgresDatabase(creds)
        case "sqlite":
            return SqliteDatabase(creds)


@pytest.fixture
def mock_db(request, postgresql, sqlite_db):
    db_type = request.param
    creds_dict = {}
    # returns a database instance rather than an engine

    match db_type:
        case "postgres":
            pg_creds_dict = {
                "host": postgresql.info.host,
                "drivername": "postgresql+psycopg2",
                "database": postgresql.info.dbname,
                "username": postgresql.info.user,
                "password": "",  # Not required for pytest-postgresql
                "port": postgresql.info.port,
            }

            db_instance = connect_to_test_db("postgres", pg_creds_dict)
        case "sqlite":
            load_test_db("snowflake", ":memory:")
            creds_dict = ":memory:"

            db_instance = connect_to_test_db("snowflake", creds_dict)

    return db_instance


def pytest_sessionstart():
    from server.controllers.workspace import AppFolderController, create_file, create_folder

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
    workspace_folder_controller = WorkspaceFolderController(r_path_to_workspace=WORKSPACE_PATH)
    apps = workspace_folder_controller.get_workspace_properties()
    for one_app in apps:
        if one_app["name"] == TEST_APP_NAME:
            apps.remove(one_app)

    workspace_folder_controller.write_workspace_properties(
        {
            "apps": apps,
        }
    )
