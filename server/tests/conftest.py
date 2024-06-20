import os
import shutil

import pytest
from fastapi.testclient import TestClient

from server.main import app

WORKSPACE_PATH = "workspace/"
BACKUP_WORKSPACE_PATH = "workspace_bu/"
TEST_WORKSPACE_PATH = "server/tests/workspace/"


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def test_workspace():
    # backup workspace
    os.rename(WORKSPACE_PATH, BACKUP_WORKSPACE_PATH)
    shutil.copytree(TEST_WORKSPACE_PATH, WORKSPACE_PATH, dirs_exist_ok=True)
    yield
    # delete workspace modified by test
    shutil.rmtree(WORKSPACE_PATH)
    # restore backup
    os.rename(BACKUP_WORKSPACE_PATH, WORKSPACE_PATH)
