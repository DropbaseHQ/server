from server.tests.constants import TEST_APP_NAME, TEST_PAGE_NAME


def get_test_ui():
    return f"""from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context


def test_ui(state: State, context: Context) -> Context:
    print("test")
    return context"""


def get_test_data_fetcher():
    return f"""import pandas as pd
from workspace.{TEST_APP_NAME}.{TEST_PAGE_NAME} import State, Context

def test_data_fetcher(state: State) -> pd.DataFrame:
    return pd.DataFrame(data=[[1]], columns=["x"])"""
