from __future__ import annotations

import pandas as pd
from sqlalchemy import Engine, create_engine


def df_to_sql(
    df: pd.DataFrame,
    con: str | Engine,
    table: str,
    *,
    if_exists: str = "append",
    dtype: dict | None = None,
    **engine_kwargs,
) -> None:
    """
    Persists a ChemInformant DataFrame to an SQL database table.

    This function provides a convenient way to store chemical data retrieved
    from get_properties() into various SQL databases. Supports SQLite, PostgreSQL,
    MySQL, and other SQLAlchemy-compatible databases.

    Args:
        df: DataFrame from get_properties() or similar ChemInformant functions
        con: Database connection string (e.g., "sqlite:///chemicals.db")
             or existing SQLAlchemy Engine object
        table: Name of the SQL table to create/write to
        if_exists: Action when table exists - "fail", "replace", or "append"
        dtype: Dictionary specifying SQL types for specific columns
        **engine_kwargs: Additional arguments passed to create_engine()

    Examples:
        >>> # Get chemical data
        >>> df = get_properties(["aspirin", "caffeine"], properties=["molecular_weight", "xlogp"])

        >>> # Save to SQLite database
        >>> df_to_sql(df, "sqlite:///my_chemicals.db", "compounds")

        >>> # Save to PostgreSQL with specific types
        >>> df_to_sql(df, "postgresql://user:pass@localhost/db", "chemicals",
        ...           dtype={"molecular_weight": "REAL", "xlogp": "REAL"})

    Note:
        - Automatically handles ChemInformant's snake_case column names
        - Use if_exists="replace" to overwrite existing tables
        - For large datasets, consider using chunks or specialized bulk loaders
    """
    # If 'con' is a string, create a new engine.
    # Otherwise, assume it's an existing engine.
    if isinstance(con, str):
        engine = create_engine(con, future=True, **engine_kwargs)
    else:
        engine = con

    df.to_sql(table, engine, index=False, if_exists=if_exists, dtype=dtype)
