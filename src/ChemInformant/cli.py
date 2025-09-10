# src/ChemInformant/cli.py (UPDATED)

from __future__ import annotations

import argparse
import sys

# Use relative import because cli.py is inside the ChemInformant package
from .cheminfo_api import (
    draw_compound,
    get_properties,
)
from .constants import ALL_PROPS
from .models import AmbiguousIdentifierError, NotFoundError

# --- NEUE ERGÄNZUNG: Importieren der SQL-Helferfunktion ---
from .sql import df_to_sql

# ----------------------------------------------------


def main_fetch():
    """
    Main entry point for the chemfetch command-line tool.

    Provides a command-line interface for retrieving chemical data from PubChem
    with support for multiple output formats including CSV, JSON, and SQL databases.
    Supports all ChemInformant features including batch processing, property selection,
    and the new snake_case standardized format.

    Command format:
        chemfetch [identifiers...] [options]

    Key features:
        - Multiple output formats: CSV, JSON, SQL database
        - Property selection: --props for specific properties
        - Batch modes: --all-properties, --include-3d
        - Direct SQL export: --format sql -o database.db
        - Error handling: Shows failed lookups with status information

    Examples:
        # Basic usage - core properties to CSV
        chemfetch aspirin caffeine

        # Specific properties to JSON
        chemfetch aspirin --props molecular_weight,xlogp --format json

        # All properties to SQL database
        chemfetch aspirin caffeine --all-properties --format sql -o chemicals.db

        # Include 3D descriptors
        chemfetch aspirin --include-3d --format csv -o results.csv
    """
    sorted(ALL_PROPS)

    parser = argparse.ArgumentParser(
        prog="chemfetch",
        description="ChemInformant: A command-line tool to fetch chemical data from PubChem.",
        epilog="Example: chemfetch aspirin caffeine --props cas,molecular_weight --format sql -o results.db",
    )

    parser.add_argument(
        "identifiers",
        nargs="+",
        help="One or more chemical identifiers (Name, CID, or SMILES string).",
    )

    parser.add_argument(
        "--props", "-p",
        type=str,
        default=None,
        help="Comma-separated list of properties (e.g., 'molecular_weight,xlogp'). If not provided, returns default core property set."
    )
    # Add new command line arguments
    parser.add_argument(
        "--include-3d",
        action="store_true",
        help="Include 3D properties in addition to the default core set."
    )
    parser.add_argument(
        "--all-properties",
        action="store_true",
        help="Retrieve all ~40 available standard properties from PubChem."
    )

    parser.add_argument(
        "-f",
        "--format",
        # --- NEUE ERGÄNZUNG: 'sql' als Formatoption hinzugefügt ---
        choices=["table", "csv", "json", "sql"],
        # ----------------------------------------------------
        default="table",
        help="Output format. Defaults to 'table'. Use 'sql' to save to a SQLite database.",
    )

    # --- NEUE ERGÄNZUNG: Output-Argument für SQL- und andere Dateiformate hinzugefügt ---
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. Required when format is 'sql'.",
    )
    # ------------------------------------------------------------------------

    args = parser.parse_args()

    # --- NEUE ERGÄNZUNG: Überprüfen, ob --output für SQL bereitgestellt wird ---
    if args.format == "sql" and not args.output:
        parser.error("--output is required when using --format=sql")
    # ----------------------------------------------------------------

    try:
        # Call the core API function with new parameters
        df = get_properties(
            args.identifiers,
            properties=args.props,
            include_3d=args.include_3d,
            all_properties=args.all_properties,
        )

        if df.empty:
            print("No data returned.", file=sys.stderr)
            return

        # Output the results based on the user's chosen format
        if args.format == "csv":
            print(df.to_csv(index=False))
        elif args.format == "json":
            print(df.to_json(orient="records", indent=2))
        # --- NEUE ERGÄNZUNG: Logik zum Speichern in einer SQL-Datenbank ---
        elif args.format == "sql":
            db_uri = f"sqlite:///{args.output}"
            table_name = "results"  # Standard-Tabellenname
            print(
                f"Writing data to table '{table_name}' in database '{args.output}'...",
                file=sys.stderr,
            )
            # Aufruf Ihrer zuvor erstellten Funktion
            df_to_sql(df, con=db_uri, table=table_name, if_exists="replace")
            print("Done.", file=sys.stderr)
        # ----------------------------------------------------------
        else:  # table
            print(df.to_string(index=False))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def main_draw():
    """
    Main entry point for the chemdraw command-line tool.

    Provides a simple command-line interface for visualizing 2D chemical structures
    directly from the terminal. Fetches structure images from PubChem and displays
    them using matplotlib.

    Command format:
        chemdraw [identifier]

    Features:
        - Accepts any ChemInformant identifier (name, CID, SMILES)
        - Displays structure with compound name as title
        - Requires matplotlib and PIL (install with: pip install ChemInformant[plot])
        - High-quality PNG images from PubChem

    Examples:
        # Visualize by name
        chemdraw aspirin

        # Visualize by CID
        chemdraw 2244

        # Visualize by SMILES
        chemdraw "CC(=O)OC1=CC=CC=C1C(=O)O"
    """
    parser = argparse.ArgumentParser(
        prog="chemdraw",
        description="Draws the 2D structure of a chemical compound using PubChem.",
    )
    parser.add_argument(
        "identifier", help="A single chemical identifier (Name, CID, or SMILES string)."
    )
    args = parser.parse_args()

    try:
        print(
            f"Attempting to draw structure for '{args.identifier}'...", file=sys.stderr
        )
        # Call the drawing function
        draw_compound(args.identifier)
    except (NotFoundError, AmbiguousIdentifierError) as e:
        # Catch specific, known exceptions from our library.
        print(f"[ChemInformant] Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors.
        print(
            f"[ChemInformant] An unexpected error occurred: {type(e).__name__} - {e}",
            file=sys.stderr,
        )
        sys.exit(1)
