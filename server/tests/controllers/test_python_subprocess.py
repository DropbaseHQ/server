import unittest.mock


def test_run_task_function_not_found():
    # Arrange
    mock_child_conn = unittest.mock.MagicMock()
    from server.controllers.python_subprocess import run_task

    # Act
    run_task(mock_child_conn, "random nonexistent function", [])

    # Assert
    status_code, stdout, output = mock_child_conn.send.call_args.args[0]
    assert status_code != 200
    assert stdout == ""
    assert "KeyError" in output
