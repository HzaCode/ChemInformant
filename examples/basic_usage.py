import sys
import os
import time

try:
    # Specify an alias for convenience
    import ChemInformant as ci
except ImportError as e:
    print(f"Import Error: {e}")
    print("Could not import 'ChemInformant'.")
    print(
        "Please ensure you have installed the package by running 'pip install .' in the project root directory."
    )
    sys.exit(1)

# Optional: Configure caching
# Default cache file is 'pubchem_cache.sqlite' in the current directory, expires after 7 days.
# To change settings (e.g., use memory cache, expire after 1 hour), uncomment the line below:
# ci.setup_cache(backend='memory', expire_after=3600)
# print(f"Using cache file (default): {os.path.abspath('pubchem_cache.sqlite')}") # Show default path


def print_separator(title=""):
    """Prints a formatted separator line to improve output readability."""
    width = 80
    if title:
        print(f"\n--- {title} {'-' * (width - len(title) - 5)}")
    else:
        print("\n" + "-" * width)


def demonstrate_single_compound(compound_identifier):
    """Gets and prints detailed information for a single compound."""
    print_separator(
        f"Single Query: {compound_identifier} (Type: {type(compound_identifier).__name__})"
    )

    try:
        # Call functions using the 'ci' alias
        print("Attempting to get individual properties:")
        # Note: ci.cid() aims to find a single, best-matching CID.
        # For more complex cases, like ambiguity, ci.info() might provide more detailed information.
        print(f"  (Note: ci.cid() attempts to find a single, best-matching CID. More complex cases like ambiguity might be detailed by ci.info().)")
        start_time_cid = time.perf_counter()
        compound_cid = ci.cid(compound_identifier)
        end_time_cid = time.perf_counter()
        print(f"  - Calling ci.cid() took: {end_time_cid - start_time_cid:.4f}s")

        if compound_cid is None:
            print(
                f"  - ci.cid() did not return a definitive CID for '{compound_identifier}'."
            )
            print("  - Attempting diagnostic ci.info() call for more details...")
            try:
                # The call to ci.info() here is primarily to leverage specific errors it might throw
                # (like NotFoundError, AmbiguousIdentifierError) to help understand why the ci.cid() call failed.
                # The result of this specific ci.info() call is not directly used for subsequent processing here.
                ci.info(compound_identifier)
                print("  - Diagnostic ci.info() call did not raise a specific error, but CID remains unresolved.")
            except (ci.NotFoundError, ci.AmbiguousIdentifierError) as specific_error: # Keep handling for AmbiguousIdentifierError
                print(f"  - Specific error from diagnostic ci.info() call: {specific_error}")
            except Exception as unknown_error:
                print(f"  - Encountered unknown error during diagnostic ci.info() check: {unknown_error}")
            print("  - Cannot proceed with fetching properties by CID.")
            return  # If CID is not resolved, cannot proceed to fetch other properties

        print(f"  - Resolved CID via ci.cid(): {compound_cid}")

        # Fetch other properties using the obtained CID
        print("\n  Fetching individual properties using the resolved CID:")
        start_time_cas = time.perf_counter()
        compound_cas = ci.cas(compound_cid)
        end_time_cas = time.perf_counter()
        print(
            f"  - CAS (from CID {compound_cid}): {compound_cas} (Query took: {end_time_cas - start_time_cas:.4f}s)"
        )

        compound_formula = ci.form(compound_cid)
        print(f"  - Formula (from CID {compound_cid}): {compound_formula}")

        compound_weight = ci.wgt(compound_cid)
        print(
            f"  - Weight (from CID {compound_cid}): {compound_weight:.2f}"
            if compound_weight is not None
            else "N/A"
        )

        compound_smiles = ci.smi(compound_cid)
        print(f"  - SMILES (from CID {compound_cid}): {compound_smiles}")

        # Get the full CompoundData object using the original identifier.
        # This demonstrates how ci.info() handles cases where the original identifier might be ambiguous.
        print(f"\n  Attempting to get full info object by calling ci.info('{compound_identifier}'):")
        start_time_info = time.perf_counter()
        compound_info: ci.CompoundData = ci.info(
            compound_identifier
        )
        end_time_info = time.perf_counter()
        print(f"  - Calling ci.info('{compound_identifier}') took: {end_time_info - start_time_info:.4f}s")

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

        # Call ci.fig() to attempt displaying the structure image
        print("\n  Attempting to display 2D structure image using ci.fig():")
        try:
            # ci.fig() is expected to handle image display internally,
            # and may print its own status messages.
            # It might not return a URL for this script to print.
            # Ensure compound_cid is valid before calling.
            if compound_cid is not None:
                ci.fig(compound_cid)
                print("    Called ci.fig(). Check console/output for image display status or image window.")
            else:
                print("    Skipped calling ci.fig() as compound_cid is None.")
        except AttributeError:
            # Handle cases where the .fig() method might not exist in the library version.
            print("    Function 'ci.fig()' not found in the library. This feature might not be available.")
        except Exception as e_fig:
            # Handle other potential errors during the .fig() call.
            print(f"    Error calling ci.fig(): {type(e_fig).__name__}: {e_fig}")
        # End of structure information demonstration

    # Catch specific errors defined by ChemInformant
    except ci.NotFoundError as e:
        print(f"  Error (NotFound): {e}")
    except ci.AmbiguousIdentifierError as e: # Keep handling logic for AmbiguousIdentifierError
        print(
            f"  Error (Ambiguous): Identifier '{e.identifier}' is ambiguous, maps to CIDs: {e.cids}"
        )
        # Example: Logic to handle ambiguity by trying the first CID
        if e.cids:
            first_cid = e.cids[0]
            print(
                f"  Attempting to requery ci.info() with the first CID ({first_cid})..."
            )
            try:
                specific_info = ci.info(first_cid)  # Query using the specific CID
                print(
                    f"  Requery successful: Name={specific_info.common_name}, Formula={specific_info.molecular_formula}"
                )
            except Exception as e_retry:
                print(f"  Requery failed: {type(e_retry).__name__}: {e_retry}")
    # Catch other potential unexpected errors from the library or network
    except Exception as e:
        print(f"  An unexpected error occurred: {type(e).__name__}: {e}")
        import traceback
        print("------ Traceback ------")
        traceback.print_exc()
        print("-----------------------")


def demonstrate_batch():
    """Demonstrates batch retrieval functionality."""
    print_separator("Batch Retrieval Example")
    identifiers = [
        "Water",    # Common name, expected to be found
        2244,       # CID for Aspirin, should be found
        "NonExistentCompoundXYZ123", # Should result in NotFoundError
        "Ethanol",  # Common name, expected to be found
        "Benzene",  # Common name, expected to be found
        "AmbiguousDrug", # Keep this item for ambiguity demonstration
    ]

    print(f"Input identifier list for batch processing: {identifiers}")
    start_time_batch = time.perf_counter()
    results = ci.get_multiple_compounds(
        identifiers
    )
    end_time_batch = time.perf_counter()
    print(
        f"\nCalling ci.get_multiple_compounds() took: {end_time_batch - start_time_batch:.4f}s"
    )

    print(f"\nBatch query results ({len(results)} results for {len(identifiers)} inputs):")
    for identifier, result in results.items():
        id_repr = repr(identifier) # Use repr() to clearly display the original identifier
        if isinstance(result, ci.CompoundData):
            print(
                f"  - {id_repr:<30}: Success - CID={result.cid:<5} Formula={result.molecular_formula:<12} CAS={result.cas if result.cas else 'N/A'}"
            )
        elif isinstance(
            result, ci.AmbiguousIdentifierError # Keep handling logic for AmbiguousIdentifierError
        ):
            print(f"  - {id_repr:<30}: Failed - Ambiguous, maps to CIDs {result.cids}")
        elif isinstance(result, ci.NotFoundError):
            print(f"  - {id_repr:<30}: Failed - Not Found")
        elif isinstance(result, (ValueError, TypeError)): # Catch invalid input type or value errors
            print(f"  - {id_repr:<30}: Failed - Invalid input: {type(result).__name__}: {result}")
        elif isinstance(
            result, Exception
        ): # Catch other retrieval or processing errors for a specific identifier
            print(
                f"  - {id_repr:<30}: Failed - Unexpected error during processing: {type(result).__name__}: {result}"
            )
        else: # Safeguard against unexpected result types
            print(f"  - {id_repr:<30}: Failed - Unknown result type in batch: {type(result)}")


if __name__ == "__main__":
    try:
        print(f"--- ChemInformant Demonstration (Version: {ci.__version__}) ---")
    except AttributeError: # Handle cases where __version__ might be missing
        print(f"--- ChemInformant Demonstration (Version: Unknown) ---")

    cache_file = os.path.abspath("pubchem_cache.sqlite")
    print(f"Default cache file location: {cache_file}")
    print("Tip: To use a memory-based cache or change expiration, see 'ci.setup_cache()' example in the script.")


    # === Single Compound Demonstration ===
    demonstrate_single_compound("Aspirin") # Query by common name
    demonstrate_single_compound(702)      # Query by CID (Ethanol)
    demonstrate_single_compound("InvalidIdentifierNoSuchDrug") # Test "Not Found" behavior
    demonstrate_single_compound(1)        # Query by CID 1 (usually a simple compound like water or a reference substance)

    # === Batch Processing Demonstration ===
    demonstrate_batch()

    print_separator("Demonstration Complete")

    # Note on Caching Behavior
    print(
        "\nNote on Caching: Running this script again may be faster if results are cached."
    )
    print(f"The default cache file is typically: {cache_file}")
    print(f"To clear the cache, you can delete this file or use appropriate cache management functions if provided by the library.")
