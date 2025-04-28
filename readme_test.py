# readme_test.py
# Code copied directly from README.md Basic Usage section

import ChemInformant as ci
import os
import sys # Need sys for stderr in exception printing if used

# --- Optional: Configure Cache (before first API call) ---
# Default: 'pubchem_cache.sqlite' in current dir, 7 days expiry
# Example: Use in-memory cache expiring after 1 hour
# ci.setup_cache(backend='memory', expire_after=3600)

# print(f"Using cache file: {os.path.abspath('pubchem_cache.sqlite')}") # Show default path

# --- Single Compound Lookup ---
print("\n--- Single Compound Lookup (from README) ---")
try:
    # Get the full data object for Aspirin by name
    aspirin_info = ci.info("Aspirin")
    print(f"Aspirin Found:")
    print(f"  CID:            {aspirin_info.cid}")
    print(f"  Formula:        {aspirin_info.molecular_formula}")
    print(f"  Weight:         {aspirin_info.molecular_weight:.2f}")
    print(f"  CAS:            {aspirin_info.cas}")
    print(f"  IUPAC Name:     {aspirin_info.iupac_name}")
    print(f"  PubChem URL:    {aspirin_info.pubchem_url}")
    print(f"  First Synonym: {aspirin_info.synonyms[0] if aspirin_info.synonyms else 'N/A'}")

    # Get specific properties directly (using name or CID)
    ethanol_cid = ci.cid("Ethanol") # Get CID first
    if ethanol_cid:
        ethanol_weight = ci.wgt(ethanol_cid) # Use CID
        ethanol_smiles = ci.smi("Ethanol")   # Use name again (will hit cache or re-fetch)
        print(f"\nEthanol (CID: {ethanol_cid}):")
        print(f"  Weight: {ethanol_weight}")
        print(f"  SMILES: {ethanol_smiles}")
    else:
        print("\nCould not resolve Ethanol CID.")

    # Example: Compound not found
    print("\nTrying a non-existent compound...")
    ci.info("NonExistentCompound123ABC")

except ci.NotFoundError as e:
    print(f"  Error Caught: {e}")
except ci.AmbiguousIdentifierError as e:
    print(f"  Error Caught: Identifier '{e.identifier}' is ambiguous, maps to CIDs: {e.cids}")
    # You could potentially pick one CID and retry:
    # first_cid = e.cids[0]
    # specific_info = ci.info(first_cid)
except Exception as e:
    print(f"  An unexpected error occurred: {type(e).__name__}: {e}")


# --- Batch Compound Lookup ---
print("\n--- Batch Compound Lookup (from README) ---")

# Identifiers list copied from the README example
identifiers_to_lookup = [
    "Water",                  # Name, Success
    2244,                     # CID (Aspirin), Success
    "Glucose",                # Name, Success (or Ambiguous depending on PubChem)
    "NonExistentCompoundXYZ", # Name, Not Found
    "AmbiguousDrug",          # Name, Ambiguous (if mock data setup like tests) - Assuming not found here
    -1,                       # Invalid CID input (ValueError)
    702                       # CID (Ethanol), Success
]

# Dictionary to store results
results = {}
try:
    results = ci.get_multiple_compounds(identifiers_to_lookup)
except Exception as e:
     print(f"Error during get_multiple_compounds call itself: {type(e).__name__}: {e}", file=sys.stderr)

print(f"\nBatch Results ({len(results)} entries):")
# Processing loop copied from README example
for identifier, result in results.items():
    id_repr = repr(identifier) # Show if input was str or int
    if isinstance(result, ci.CompoundData):
        print(f"  - {id_repr:<25}: Success - CID={result.cid:<5} Formula={result.molecular_formula}")
    elif isinstance(result, ci.NotFoundError):
          print(f"  - {id_repr:<25}: Failed - Not Found")
    elif isinstance(result, ci.AmbiguousIdentifierError):
          print(f"  - {id_repr:<25}: Failed - Ambiguous ({len(result.cids)} CIDs)")
    elif isinstance(result, (ValueError, TypeError)):
          print(f"  - {id_repr:<25}: Failed - Invalid Input ({type(result).__name__})")
    elif isinstance(result, Exception): # Catch other potential errors (e.g., network)
        print(f"  - {id_repr:<25}: Failed - Error during fetch ({type(result).__name__})")
    else:
        print(f"  - {id_repr:<25}: Failed - Unknown result type: {type(result)}")

# --- Caching Note (from README) ---
print("\n--- Caching Note (from README) ---")
print("Run this script again - subsequent calls for the same compounds should be much faster due to caching.")
default_cache_path = os.path.abspath('pubchem_cache.sqlite')
if os.path.exists(default_cache_path):
    print(f"Cache file is located at: {default_cache_path}")
    print("To clear the cache, simply delete this file.")
else:
      print("Default cache file ('pubchem_cache.sqlite') not created yet (or using memory cache).") 