# examples/basic_usage_en.py

import sys
import os
import time

try:
    # --- Specify the alias using the 'as ci' keyword ---
    import ChemInformant as ci
except ImportError as e:
    print(f"Import Error: {e}")
    print("Could not import 'ChemInformant'.")
    print(
        "Please ensure you have installed the package by running 'pip install .' in the project root directory."
    )
    sys.exit(1)

# --- Optional: Configure Cache ---
# Default cache is 'pubchem_cache.sqlite' in the current directory, expires after 7 days.
# If you want to change settings (e.g., use memory cache, expire after 1 hour), uncomment the line below:
# ci.setup_cache(backend='memory', expire_after=3600)
# print(f"Using cache file (default): {os.path.abspath('pubchem_cache.sqlite')}") # Show default path


def print_separator(title=""):
    """Prints a formatted separator line."""
    width = 80
    if title:
        print(f"\n--- {title} {'-' * (width - len(title) - 5)}")
    else:
        print("\n" + "-" * width)


def demonstrate_single_compound(compound_identifier):
    """Gets and prints details for a single compound, using the 'ci' alias."""
    print_separator(
        f"Single Query: {compound_identifier} (Type: {type(compound_identifier).__name__})"
    )

    try:
        # === Call functions using the ci alias ===
        print("Attempting to get individual properties:")
        start_time_cid = time.perf_counter()
        compound_cid = ci.cid(compound_identifier)  # Calling ci.cid()
        end_time_cid = time.perf_counter()
        print(f"  - Calling ci.cid() took: {end_time_cid - start_time_cid:.4f}s")

        if compound_cid is None:
            print(
                f"  - Could not definitively resolve CID for '{compound_identifier}' (maybe not found or ambiguous)"
            )
            # Try calling info() to get a more specific error
            try:
                ci.info(compound_identifier)
            except (ci.NotFoundError, ci.AmbiguousIdentifierError) as specific_error:
                print(f"  - Specific error: {specific_error}")
            except Exception as unknown_error:
                print(f"  - Encountered unknown error during check: {unknown_error}")
            return  # Cannot continue fetching other properties

        print(f"  - CID: {compound_cid}")

        # Use the obtained CID to query other properties (or query directly with name/CID)
        start_time_cas = time.perf_counter()
        compound_cas = ci.cas(compound_cid)  # Calling ci.cas()
        end_time_cas = time.perf_counter()
        print(
            f"  - CAS: {compound_cas} (Query took: {end_time_cas - start_time_cas:.4f}s)"
        )

        compound_formula = ci.form(compound_cid)  # Calling ci.form()
        print(f"  - Formula: {compound_formula}")

        compound_weight = ci.wgt(compound_cid)  # Calling ci.wgt()
        print(
            f"  - Weight: {compound_weight:.2f}"
            if compound_weight is not None
            else "N/A"
        )

        compound_smiles = ci.smi(compound_cid)  # Calling ci.smi()
        print(f"  - SMILES: {compound_smiles}")

        # Get the complete CompoundData object
        print("\n  Attempting to get full info (calling ci.info()):")
        start_time_info = time.perf_counter()
        # If the previous compound_identifier was ambiguous, this will fail again
        compound_info: ci.CompoundData = ci.info(
            compound_identifier
        )  # Calling ci.info()
        end_time_info = time.perf_counter()
        print(f"  - Calling ci.info() took: {end_time_info - start_time_info:.4f}s")

        print("  - Successfully obtained CompoundData object:")
        print(f"    Common Name: {compound_info.common_name}")
        print(f"    IUPAC Name:  {compound_info.iupac_name}")
        print(
            f"    Description snippet: {(compound_info.description[:60] + '...') if compound_info.description and len(compound_info.description) > 60 else compound_info.description}"
        )
        print(
            f"    First Synonym: {compound_info.synonyms[0] if compound_info.synonyms else 'N/A'}"
        )
        print(f"    PubChem URL: {compound_info.pubchem_url}")

    # Catch our defined specific errors
    except ci.NotFoundError as e:
        print(f"  Error: {e}")
    except ci.AmbiguousIdentifierError as e:
        print(
            f"  Error: Identifier '{e.identifier}' is ambiguous, maps to CIDs: {e.cids}"
        )
        # Logic to handle ambiguity could be added here, e.g., selecting the first CID to requery
        if e.cids:
            first_cid = e.cids[0]
            print(
                f"    Attempting to requery info() with the first CID ({first_cid})..."
            )
            try:
                specific_info = ci.info(first_cid)  # Query with the specific CID
                print(
                    f"    Requery successful: Formula={specific_info.molecular_formula}"
                )
            except Exception as e_retry:
                print(f"    Requery failed: {type(e_retry).__name__}: {e_retry}")
    # Catch other potential unexpected errors
    except Exception as e:
        print(f"  An unexpected error occurred: {type(e).__name__}: {e}")
        import traceback

        print("------ Traceback ------")
        traceback.print_exc()
        print("-----------------------")


def demonstrate_batch():
    """Demonstrates the batch retrieval function, using the 'ci' alias."""
    print_separator("Batch Retrieval Example")
    # Includes various cases: successful name, successful CID, not found, simulated ambiguous name, partial data (Water)
    identifiers = [
        "Water",
        2244,
        "Glucose",
        "NonExistentCompound",
        "Ethanol",
        "Benzene",
        "AmbiguousDrug",
    ]

    print(f"Input identifier list: {identifiers}")
    start_time_batch = time.perf_counter()
    results = ci.get_multiple_compounds(
        identifiers
    )  # Calling ci.get_multiple_compounds()
    end_time_batch = time.perf_counter()
    print(
        f"\nCalling ci.get_multiple_compounds() took: {end_time_batch - start_time_batch:.4f}s"
    )

    print(f"\nBatch query results ({len(results)}/{len(identifiers)} entries):")
    for identifier, result in results.items():
        # Use repr() to clearly display the original identifier (distinguishes '2244' from 2244)
        id_repr = repr(identifier)
        if isinstance(result, ci.CompoundData):  # Using ci.CompoundData
            # Display some key information
            print(
                f"  - {id_repr:<25}: Success - CID={result.cid:<5} Formula={result.molecular_formula:<10} CAS={result.cas}"
            )
        elif isinstance(
            result, ci.AmbiguousIdentifierError
        ):  # Using ci.AmbiguousIdentifierError
            print(f"  - {id_repr:<25}: Failed - Ambiguous, maps to CIDs {result.cids}")
        elif isinstance(result, ci.NotFoundError):  # Using ci.NotFoundError
            print(f"  - {id_repr:<25}: Failed - Not Found")
        elif isinstance(result, ValueError):  # Catch invalid input error
            print(f"  - {id_repr:<25}: Failed - Invalid input: {result}")
        elif isinstance(result, TypeError):  # Catch type error
            print(f"  - {id_repr:<25}: Failed - Type error: {result}")
        elif isinstance(
            result, Exception
        ):  # Catch other retrieval or processing errors
            print(
                f"  - {id_repr:<25}: Failed - Unexpected error: {type(result).__name__}: {result}"
            )
        else:  # Shouldn't happen, but as a safeguard
            print(f"  - {id_repr:<25}: Failed - Unknown result type: {type(result)}")


if __name__ == "__main__":
    try:
        # Accessing the version number also requires the alias
        print(f"--- ChemInformant Demonstration (v{ci.__version__}) ---")
    except (NameError, AttributeError):
        print(f"--- ChemInformant Demonstration ---")

    cache_file = os.path.abspath("pubchem_cache.sqlite")
    print(f"Cache file (default): {cache_file}")

    # === Single Compound Demonstration ===
    demonstrate_single_compound("Aspirin")
    demonstrate_single_compound(702)  # CID for Ethanol
    demonstrate_single_compound(
        "Glucose"
    )  # Check ambiguity handling (depends on current PubChem data)
    demonstrate_single_compound("NonExistentCompound123")  # Test not found

    # === Batch Processing Demonstration ===
    # Note: Batch example also includes potentially ambiguous "Glucose" and "AmbiguousDrug" (simulated)
    demonstrate_batch()

    print_separator("Demonstration Complete")

    # Add a note about caching
    print(
        "\nTip: Running this script again should be faster because results will be cached."
    )
    print(f"      The cache file is located at: {cache_file}")
    print(f"      To clear the cache, you can delete this file.")
