import unittest.mock

def test_run_task_function_not_found():
    # Arrange
    mock_child_conn = unittest.mock.MagicMock()
    from server.worker.python_subprocess import run_task

    # Act
    run_task(mock_child_conn, "random nonexistent function", [])

    # Assert
    success, stdout, output = mock_child_conn.send.call_args.args[0]
    assert not success
    assert stdout == ""
    assert "KeyError" in output