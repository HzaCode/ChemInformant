import pandas as pd
import pytest
from sqlalchemy import create_engine, func, select, table

import ChemInformant as ci

# These tests fetch data from live PubChem and are intentionally marked as
# integration tests. They are excluded from the default `pytest -m "not
# integration"` CI run so a transient PubChem hiccup does not break the
# main build. Run them locally or via the dedicated `integration` job with
# `pytest -m integration tests/`.
pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def test_data():
    """Fixture to fetch all necessary test data from PubChem once per test session."""
    print("\n(Fetching test data from PubChem...)")
    return {
        "aspirin": ci.get_properties(["aspirin"], ["cas", "xlogp"]),
        "others": ci.get_properties(["caffeine", "ibuprofen"], ["cas", "xlogp"]),
        "empty": pd.DataFrame(columns=["input_identifier", "cid", "status", "cas"]),
    }


@pytest.fixture
def in_memory_engine():
    """
    Creates a new, clean in-memory SQLite engine for each test function.
    The `yield` keyword passes the engine to the test, and the code after
    `yield` is the cleanup, which runs after the test is done.
    """
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()


TABLE_NAME = "test_table"


def test_if_exists_replace(in_memory_engine, test_data):
    """
    Tests that if_exists='replace' correctly overwrites existing data.
    """

    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]

    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME, if_exists="replace")
    count1 = pd.read_sql(
        select(func.count()).select_from(table(TABLE_NAME)), in_memory_engine
    ).iloc[0, 0]
    assert count1 == 1, "Failed to write initial data"

    ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="replace")
    count2 = pd.read_sql(
        select(func.count()).select_from(table(TABLE_NAME)), in_memory_engine
    ).iloc[0, 0]
    assert count2 == 2, "if_exists='replace' failed to overwrite data"


def test_if_exists_append(in_memory_engine, test_data):
    """
    Tests that if_exists='append' correctly adds new data without deleting old data.
    """
    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]

    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME, if_exists="replace")

    ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="append")

    total_count = pd.read_sql(
        select(func.count()).select_from(table(TABLE_NAME)), in_memory_engine
    ).iloc[0, 0]
    expected_count = len(df_aspirin) + len(df_others)
    assert total_count == expected_count, "if_exists='append' failed to add new data"


def test_if_exists_fail(in_memory_engine, test_data):
    """
    Tests that if_exists='fail' raises a ValueError when the table already exists.
    """
    df_aspirin = test_data["aspirin"]
    df_others = test_data["others"]

    ci.df_to_sql(df_aspirin, in_memory_engine, TABLE_NAME)

    with pytest.raises(ValueError, match="already exists"):
        ci.df_to_sql(df_others, in_memory_engine, TABLE_NAME, if_exists="fail")


def test_writing_empty_dataframe(in_memory_engine, test_data):
    """
    Tests that writing an empty DataFrame creates an empty table without errors.
    """
    df_empty = test_data["empty"]
    ci.df_to_sql(df_empty, in_memory_engine, TABLE_NAME, if_exists="replace")

    count = pd.read_sql(
        select(func.count()).select_from(table(TABLE_NAME)), in_memory_engine
    ).iloc[0, 0]
    assert count == 0, "Writing an empty DataFrame did not result in an empty table"
