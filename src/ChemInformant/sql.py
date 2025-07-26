from __future__ import annotations
import pandas as pd
from sqlalchemy import create_engine, Engine
from typing import Union


def df_to_sql(
    df: pd.DataFrame,
    con: Union[str, Engine],
    table: str,
    *,
    if_exists: str = "append",
    dtype: dict | None = None,
    **engine_kwargs,
) -> None:
    """
    Persists a DataFrame to an SQL table using SQLAlchemy.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be written to the database.
    con : str or sqlalchemy.engine.Engine
        A SQLAlchemy-compatible database URI (e.g., "sqlite:///mylab.db")
        OR an existing SQLAlchemy Engine object.
    table : str
        The name of the SQL table to write to.
    if_exists : {"fail", "replace", "append"}, default "append"
        ... (rest of the docstring is the same)
    """
    # If 'con' is a string, create a new engine.
    # Otherwise, assume it's an existing engine.
    if isinstance(con, str):
        engine = create_engine(con, future=True, **engine_kwargs)
    else:
        engine = con

    df.to_sql(table, engine, index=False, if_exists=if_exists, dtype=dtype)
