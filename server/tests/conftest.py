import shutil
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server.main import app

ROOT_PATH = Path(__file__).parent.parent.parent
WORKSPACE_PATH = ROOT_PATH.joinpath("workspace")


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


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
