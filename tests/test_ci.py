# tests/test_cli.py

import subprocess
import sys
import os
import pytest
import pandas as pd

# --- Path Correction ---
# Add the project root directory (which contains the 'src' folder) to the Python path
# This ensures that the test runner can find the source modules.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import the modules we need to mock and test
from src.ChemInformant import cli as chem_cli
from src.ChemInformant import cheminfo_api
from src.ChemInformant import api_helpers
from src.ChemInformant import models

def run_command(command: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    """Helper function to run a command as a subprocess and capture its output."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout
    )

# --- chemfetch Command Tests ---

def test_chemfetch_success_table_format():
    """Tests that chemfetch successfully retrieves data using a live API call."""
    proc = run_command(["chemfetch", "aspirin", "--props", "cas,molecular_weight"])
    assert proc.returncode == 0, f"Command failed with stderr: {proc.stderr}"
    output = proc.stdout
    assert "aspirin" in output and "2244" in output and "OK" in output

def test_chemfetch_handles_partial_failure_gracefully():
    """
    Verifies that chemfetch handles a mix of valid and invalid identifiers
    by returning a table with appropriate statuses using a live API call.
    """
    cmd = ["chemfetch", "caffeine", "NotARealCompound12345"]
    proc = run_command(cmd)
    assert proc.returncode == 0, f"Expected exit code 0 for partial failure, but got {proc.returncode}. Stderr: {proc.stderr}"
    output = proc.stdout
    assert "caffeine" in output and "OK" in output
    assert "NotARealCompound12345" in output and "NotFoundError" in output

def test_chemfetch_reports_ambiguous_identifier_in_status(monkeypatch, capsys):
    """
    Verifies that for an ambiguous identifier, chemfetch correctly reports the
    'AmbiguousIdentifierError' status by mocking the network-facing function.
    This test does not make a live network call.
    """
    # 1. We mock the function at the network boundary: get_cids_by_name.
    #    We make it return a list of multiple CIDs, which is the condition
    #    that should trigger the AmbiguousIdentifierError.
    monkeypatch.setattr(
        api_helpers,
        "get_cids_by_name",
        lambda name: [123, 456]  # Simulate finding multiple results
    )

    # 2. Monkeypatch sys.argv to simulate the user running the command.
    monkeypatch.setattr(sys, "argv", ["chemfetch", "any_ambiguous_name", "--props", "cas"])

    # 3. Call the main function. It will use the real `get_properties` and `_resolve_to_single_cid`,
    #    but the mocked `get_cids_by_name` will cause the correct exception to be raised internally.
    chem_cli.main_fetch()

    # 4. Assert that the captured output contains the correct status string.
    captured = capsys.readouterr()
    output = captured.out
    assert "any_ambiguous_name" in output
    assert "AmbiguousIdentifierError" in output
    assert "OK" not in output

def test_chemfetch_fails_on_invalid_property():
    """Tests that chemfetch exits with a non-zero code for an unsupported property."""
    cmd = ["chemfetch", "water", "--props", "boiling_point"]
    proc = run_command(cmd)
    assert proc.returncode != 0, "Expected a non-zero exit code for an invalid property."
    assert "Error:" in proc.stderr
    assert "Unsupported properties" in proc.stderr
# --- chemdraw Command Tests ---

def test_chemdraw_runs_successfully():
    """Tests that the chemdraw command can be invoked without crashing."""
    if os.environ.get('CI'):
        pytest.skip("Skipping GUI-based test in CI environment")
    try:
        proc = run_command(["chemdraw", "caffeine"], timeout=15)
        assert proc.returncode == 0
        assert "Attempting to draw" in proc.stderr
    except subprocess.TimeoutExpired:
        # This is an acceptable outcome in a headless CI/CD environment
        pass

def test_chemdraw_fails_gracefully_on_not_found():
    """
    Verifies that chemdraw exits with a non-zero code and a clear error message
    when an identifier is not found.
    """
    proc = run_command(["chemdraw", "NotARealCompound12345"])
    assert proc.returncode != 0, "Expected a non-zero exit code for a non-existent compound."
    assert "[ChemInformant] Error:" in proc.stderr
    assert "was not found" in proc.stderr