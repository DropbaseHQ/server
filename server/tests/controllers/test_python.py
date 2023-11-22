import unittest.mock

from server.controllers.python import run_exec_task


def test_run_exec_task():
    # Arrange
    mock_child_conn = unittest.mock.MagicMock()
    args = {
        "app_name": "dropbase_test_app",
        "page_name": "page1",
        "python_string": "def f():\n  print('test output', end='')\nf()",
        "payload": {
            "state": {"widgets": {"widget1": {}}, "tables": {"table1": {}}},
            "context": {
                "widgets": {"widget1": {"components": {}}},
                "tables": {"table1": {"columns": {}}},
            },
        },
        "file": {"name": "function1"},
    }

    # Act
    run_exec_task(mock_child_conn, args)

    # Assert
    success, stdout, output = mock_child_conn.send.call_args.args[0]
    assert success
    assert stdout == "test output"
    assert output == None
