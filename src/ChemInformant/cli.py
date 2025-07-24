# src/ChemInformant/cli.py (UPDATED)

from __future__ import annotations

import argparse
import sys

# Use relative import because cli.py is inside the ChemInformant package
from .cheminfo_api import (
    get_properties,
    draw_compound,
    PROPERTY_ALIASES,
    _SPECIAL_PROPS,
)
from .models import NotFoundError, AmbiguousIdentifierError

# --- NEUE ERGÄNZUNG: Importieren der SQL-Helferfunktion ---
from .sql import df_to_sql

# ----------------------------------------------------


def main_fetch():
    """
    Main entry point for the chemfetch command.
    """
    available_props = sorted(list(PROPERTY_ALIASES.keys()) + list(_SPECIAL_PROPS))

    parser = argparse.ArgumentParser(
        prog="chemfetch",
        description="ChemInformant: A command-line tool to fetch chemical data from PubChem.",
        epilog=f"Example: chemfetch aspirin caffeine --props cas,molecular_weight --format sql -o results.db",
    )

    parser.add_argument(
        "identifiers",
        nargs="+",
        help="One or more chemical identifiers (Name, CID, or SMILES string).",
    )

    parser.add_argument(
        "--props",
        default="cas,molecular_weight,iupac_name",
        help=(
            "Comma-separated list of properties to fetch. "
            f"Defaults to 'cas,molecular_weight,iupac_name'. "
            f"Available: {', '.join(available_props)}"
        ),
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
        properties_list = [prop.strip() for prop in args.props.split(",")]

        # Call the core API function
        df = get_properties(args.identifiers, properties_list)

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
    Main entry point for the chemdraw command.
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
