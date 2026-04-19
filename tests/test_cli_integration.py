# tests/test_cli_integration.py
#
# Live CLI integration tests. These tests invoke the real chemfetch / chemdraw
# entry points against the live PubChem API and are therefore marked as
# `integration`. They are excluded from the default unit-test matrix:
#
#   pytest -m "not integration" tests/
#
# and only run in the dedicated integration job:
#
#   pytest -m integration tests/

import os
import sqlite3
import subprocess
import sys
from typing import Optional

import pandas as pd
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ChemInformant import api_helpers
from ChemInformant import cli as chem_cli

pytestmark = pytest.mark.integration


def run_command(
    command: str, *args: str, timeout: Optional[int] = None
) -> subprocess.CompletedProcess:
    """Helper function to run a command as a subprocess and capture its output."""
    return subprocess.run(
        [command, *args], capture_output=True, text=True, check=False, timeout=timeout
    )


def is_pubchem_available() -> bool:
    """Check if PubChem API is available.

    Called only from the session-scoped autouse fixture below, so the network
    request happens at test *execution* time (after -m filtering), not at
    collection/import time.
    """
    try:
        response = requests.get(
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/water/cids/JSON",
            timeout=5,
        )
        return response.status_code == 200 and "IdentifierList" in response.text
    except Exception:
        return False


@pytest.fixture(scope="session", autouse=True)
def _require_pubchem_available() -> None:
    """Skip live CLI integration tests if PubChem is unavailable.

    This fixture runs only when the `integration` marker is selected; default
    unit runs deselect the whole module before the fixture ever executes.
    """
    if not is_pubchem_available():
        pytest.skip("PubChem API is under maintenance or unavailable")


# --- chemfetch Command Tests ---


def test_chemfetch_success_table_format() -> None:
    """Tests that chemfetch successfully retrieves data using a live API call."""
    proc = run_command("chemfetch", "water", "--props", "cas,molecular_formula")
    assert proc.returncode == 0, f"Command failed with stderr: {proc.stderr}"
    output = proc.stdout
    assert "water" in output
    assert "7732-18-5" in output  # CAS for water
    assert "H2O" in output  # Formula for water


def test_chemfetch_handles_partial_failure_gracefully() -> None:
    """
    Verifies that chemfetch handles a mix of valid and invalid identifiers
    by returning a table with appropriate statuses using a live API call.
    """
    proc = run_command("chemfetch", "caffeine", "NotARealCompound12345")
    assert proc.returncode == 0, (
        f"Expected exit code 0 for partial failure, but got {proc.returncode}. Stderr: {proc.stderr}"
    )
    output = proc.stdout
    assert "caffeine" in output and "OK" in output
    assert "NotARealCompound12345" in output and "NotFoundError" in output


def test_chemfetch_reports_ambiguous_identifier_in_status(monkeypatch, capsys) -> None:
    """
    Verifies that for an ambiguous identifier, chemfetch correctly reports the
    'AmbiguousIdentifierError' status by mocking the network-facing function.
    This particular assertion does not make a live network call, but lives in
    the integration module because it exercises the real CLI entry point.
    """
    monkeypatch.setattr(api_helpers, "get_cids_by_name", lambda name: [123, 456])
    monkeypatch.setattr(
        sys, "argv", ["chemfetch", "any_ambiguous_name", "--props", "cas"]
    )
    chem_cli.main_fetch()
    captured = capsys.readouterr()
    output = captured.out
    assert "any_ambiguous_name" in output
    assert "AmbiguousIdentifierError" in output
    assert "OK" not in output


def test_chemfetch_fails_on_invalid_property() -> None:
    """Tests that chemfetch exits with a non-zero code for an unsupported property."""
    proc = run_command("chemfetch", "water", "--props", "boiling_point")
    assert proc.returncode != 0, (
        "Expected a non-zero exit code for an invalid property."
    )
    assert "Error:" in proc.stderr
    assert "Unsupported properties" in proc.stderr


# --- SQL output tests ---


def test_chemfetch_sql_output_success(tmp_path) -> None:
    """
    Verifies that `chemfetch --format sql` successfully creates a database
    file with the correct data.
    """
    db_file = tmp_path / "test_output.db"

    proc = run_command(
        "chemfetch",
        "caffeine",
        "--props",
        "cas,molecular_weight",
        "--format",
        "sql",
        "-o",
        str(db_file),
    )

    assert proc.returncode == 0, f"Command failed with stderr: {proc.stderr}"
    assert "Writing data to table" in proc.stderr, (
        "Success message not found in stderr."
    )

    assert db_file.exists(), "Database file was not created."

    con = sqlite3.connect(db_file)
    df = pd.read_sql_query("SELECT * FROM results", con)
    con.close()

    assert df.shape[0] == 1
    assert "cas" in df.columns
    assert "molecular_weight" in df.columns
    assert df.loc[0, "input_identifier"] == "caffeine"
    assert df.loc[0, "cas"] == "58-08-2"


def test_chemfetch_sql_fails_without_output_path() -> None:
    """
    Verifies that `chemfetch --format sql` fails with a clear error
    message if the --output/-o argument is not provided.
    """
    proc = run_command("chemfetch", "water", "--format", "sql")

    assert proc.returncode != 0, "Expected a non-zero exit code for missing argument."

    assert "--output is required" in proc.stderr, (
        "Expected error message for missing --output not found."
    )


# --- chemdraw Command Tests ---


def test_chemdraw_runs_successfully() -> None:
    """Tests that the chemdraw command can be invoked without crashing."""
    if os.environ.get("CI"):
        pytest.skip("Skipping GUI-based test in CI environment")
    try:
        proc = run_command("chemdraw", "caffeine", timeout=15)
        assert proc.returncode == 0
        assert "Attempting to draw" in proc.stderr
    except subprocess.TimeoutExpired:
        pytest.skip("chemdraw command timed out, likely waiting for user interaction")


def test_chemdraw_fails_gracefully_on_not_found() -> None:
    """
    Verifies that chemdraw exits with a non-zero code and a clear error message
    when an identifier is not found.
    """
    proc = run_command("chemdraw", "NotARealCompound12345")
    assert proc.returncode != 0, (
        "Expected a non-zero exit code for a non-existent compound."
    )
    assert "[ChemInformant] Error:" in proc.stderr
    assert "was not found" in proc.stderr
