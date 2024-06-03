from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME


def get_test_ui():
    return f"""from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context


def test_ui(state: State, context: Context) -> Context:
    context.page.message = "Test page message"
    return context
"""


def get_test_data_fetcher():
    return f"""from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context
import pandas as pd


def test_data_fetcher(state: State, context: Context) -> Context:
    df = pd.DataFrame({{"a": [1, 2, 3]}})
    context.table1.data = df.to_dtable()
    return context"""
