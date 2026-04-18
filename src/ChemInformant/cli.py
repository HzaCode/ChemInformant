from __future__ import annotations

import argparse
import sys

from .cheminfo_api import (
    draw_compound,
    get_properties,
)
from .constants import ALL_PROPS
from .models import AmbiguousIdentifierError, NotFoundError
from .sql import df_to_sql


def main_fetch() -> None:
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
        "--props",
        "-p",
        type=str,
        default=None,
        help="Comma-separated list of properties (e.g., 'molecular_weight,xlogp'). If not provided, returns default core property set.",
    )
    parser.add_argument(
        "--include-3d",
        action="store_true",
        help="Include 3D properties in addition to the default core set.",
    )
    parser.add_argument(
        "--all-properties",
        action="store_true",
        help="Retrieve all ~40 available standard properties from PubChem.",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["table", "csv", "json", "sql"],
        default="table",
        help="Output format. Defaults to 'table'. Use 'sql' to save to a SQLite database.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file path. Required when format is 'sql'.",
    )

    args = parser.parse_args()

    try:
        df = get_properties(
            args.identifiers,
            properties=args.props,
            include_3d=args.include_3d,
            all_properties=args.all_properties,
        )

        if df.empty:
            print("No data returned.", file=sys.stderr)
            return

        def _emit_output(text: str, output: str | None) -> None:
            """Write output to file if specified, otherwise print to stdout."""
            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(text)
                    if not text.endswith("\n"):
                        f.write("\n")
                print(f"Output written to: {output}", file=sys.stderr)
            else:
                print(text)

        if args.format == "csv":
            _emit_output(df.to_csv(index=False), args.output)
        elif args.format == "json":
            _emit_output(df.to_json(orient="records", indent=2), args.output)
        elif args.format == "sql":
            if not args.output:
                parser.error("--output is required when using --format=sql")
            db_uri = f"sqlite:///{args.output}"
            table_name = "results"
            print(
                f"Writing data to table '{table_name}' in database '{args.output}'...",
                file=sys.stderr,
            )
            df_to_sql(df, con=db_uri, table=table_name, if_exists="replace")
            print("Done.", file=sys.stderr)
        else:  # table
            _emit_output(df.to_string(index=False), args.output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def main_draw() -> None:
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
