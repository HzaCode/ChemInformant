
# ChemInformant

![ChemInformant Logo](https://github.com/HzaCode/ChemInformant/blob/main/doc/image/logo.jpg?raw=true)


**ChemInformant** is a Python library designed for streamlined access to chemical data from the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database. It simplifies retrieving compound information by providing:

* **Automatic Caching:** Uses `requests-cache` to avoid redundant API calls and speed up repeated queries.
* **Data Validation:** Employs `pydantic` models (`CompoundData`) to ensure retrieved data is structured and typed correctly.
* **Robust Error Handling:** Gracefully handles cases where compounds are not found (`NotFoundError`) or identifiers are ambiguous (`AmbiguousIdentifierError`).
* **Convenience Functions:** Offers simple functions (`cid`, `cas`, `form`, `wgt`, etc.) to fetch specific properties.
* **Batch Processing:** Efficiently retrieves data for multiple compounds in a single call (`get_multiple_compounds`).
* **Partial Data Retrieval:** Attempts to return as much data as possible even if some underlying API calls fail for a specific compound.

## Key Features

* Look up compounds by name or PubChem CID.
* Retrieve comprehensive compound details (`info`) or specific properties (`cas`, `unii`, `molecular_formula`, `molecular_weight`, `canonical_smiles`, `iupac_name`, `description`, `synonyms`).
* Automatic caching of API responses to disk (default: `pubchem_cache.sqlite`) or memory.
* Configurable cache expiration time (default: 7 days).
* Clear distinction between "not found" and "ambiguous identifier" errors.
* Efficient batch retrieval for lists of identifiers.
* Validated and typed data output via the `CompoundData` model.
* Computed `pubchem_url` property on the `CompoundData` model.

## Installation

Install the latest stable version from PyPI:

```bash
pip install ChemInformant

```
Or, install directly from the GitHub repository (for the latest development version):

```bash
pip install git+https://github.com/HzaCode/ChemInformant.git

```

For editable installs :
```bash
# Clone the repository first if you haven't
 git clone https://github.com/HzaCode/ChemInformant.git
 cd ChemInformant

pip install -e .
```

## Basic Usage

The recommended way to use the library is by importing it with the alias `ci`.

```python
import ChemInformant as ci
import os

# --- Optional: Configure Cache (before first API call) ---
# Default: 'pubchem_cache.sqlite' in current dir, 7 days expiry
# Example: Use in-memory cache expiring after 1 hour
# ci.setup_cache(backend='memory', expire_after=3600)

# print(f"Using cache file: {os.path.abspath('pubchem_cache.sqlite')}") # Show default path

# --- Single Compound Lookup ---
print("\n--- Single Compound Lookup ---")
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
print("\n--- Batch Compound Lookup ---")
identifiers_to_lookup = [
    "Water",                  # Name, Success
    2244,                     # CID (Aspirin), Success
    "Glucose",                # Name, Success (or Ambiguous depending on PubChem)
    "NonExistentCompoundXYZ", # Name, Not Found
    "AmbiguousDrug",          # Name, Ambiguous (if mock data setup like tests)
    -1,                       # Invalid CID input (ValueError)
    702                       # CID (Ethanol), Success
]

results = ci.get_multiple_compounds(identifiers_to_lookup)

print(f"\nBatch Results ({len(results)} entries):")
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

# --- Caching ---
print("\n--- Caching Note ---")
print("Run this script again - subsequent calls for the same compounds should be much faster due to caching.")
default_cache_path = os.path.abspath('pubchem_cache.sqlite')
if os.path.exists(default_cache_path):
    print(f"Cache file is located at: {default_cache_path}")
    print("To clear the cache, simply delete this file.")
else:
      print("Default cache file ('pubchem_cache.sqlite') not created yet (or using memory cache).")
```

## API Overview

### Primary Functions

* **`ci.info(name_or_cid: Union[str, int]) -> CompoundData`**:
  * The main function to get comprehensive data for a single compound.
  * Takes a compound name (string) or PubChem CID (integer).
  * Returns a `CompoundData` object on success.
  * Raises `NotFoundError` if the identifier isn't found.
  * Raises `AmbiguousIdentifierError` if a name maps to multiple CIDs.
  * Raises `ValueError` for invalid CIDs (e.g., <= 0).
  * Raises `TypeError` for invalid input types.
  * Attempts to return partial data if some underlying API calls fail, printing warnings to `stderr`.

* **`ci.get_multiple_compounds(identifiers: List[Union[str, int]]) -> Dict[Union[str, int], Union[CompoundData, Exception]]`**:
  * Retrieves data for a list of identifiers efficiently using batch API calls where possible.
  * Returns a dictionary where keys are the original identifiers from the input list.
  * Values are either:
    * A `CompoundData` object on success.
    * An `Exception` instance (`NotFoundError`, `AmbiguousIdentifierError`, `ValueError`, `TypeError`, or potentially a `requests.exceptions.RequestException` if a batch fetch fails) indicating the reason for failure for that specific identifier.

### Convenience Functions

These functions provide quick access to specific properties. They internally call `ci.info()` and handle errors by returning `None` (or an empty list for `syn`) if the compound is not found, ambiguous, or if an error occurs during data retrieval.

* `ci.cid(name_or_cid) -> Optional[int]`: Gets the unambiguous CID.
* `ci.cas(name_or_cid) -> Optional[str]`: Gets the CAS Registry Number.
* `ci.unii(name_or_cid) -> Optional[str]`: Gets the FDA UNII code.
* `ci.form(name_or_cid) -> Optional[str]`: Gets the Molecular Formula.
* `ci.wgt(name_or_cid) -> Optional[float]`: Gets the Molecular Weight (as float).
* `ci.smi(name_or_cid) -> Optional[str]`: Gets the Canonical SMILES string.
* `ci.iup(name_or_cid) -> Optional[str]`: Gets the IUPAC Name.
* `ci.dsc(name_or_cid) -> Optional[str]`: Gets the compound description text.
* `ci.syn(name_or_cid) -> List[str]`: Gets the list of synonyms (returns `[]` on failure).

### Data Model

* **`ci.CompoundData`**: A `pydantic` `BaseModel` representing the compound information. Key fields include:
  * `cid: int`
  * `input_identifier: Union[str, int]`
  * `common_name: Optional[str]`
  * `cas: Optional[str]`
  * `unii: Optional[str]`
  * `molecular_formula: Optional[str]`
  * `molecular_weight: Optional[float]`
  * `canonical_smiles: Optional[str]`
  * `iupac_name: Optional[str]`
  * `description: Optional[str]`
  * `synonyms: List[str]`
  * `pubchem_url: Optional[HttpUrl]` (Computed property)

### Exceptions

* **`ci.NotFoundError(identifier)`**: Raised when a compound identifier cannot be found in PubChem. Access the identifier via `e.identifier`.
* **`ci.AmbiguousIdentifierError(identifier, cids)`**: Raised when a compound name maps to multiple CIDs. Access the identifier via `e.identifier` and the list of CIDs via `e.cids`.

### Cache Configuration

* **`ci.setup_cache(cache_name='pubchem_cache', backend='sqlite', expire_after=604800, **kwargs)`**:
  * Call this *before* any other `ci` function if you need non-default cache settings.
  * `cache_name`: Name of the cache file (for `sqlite`) or namespace (for `redis`, etc.).
  * `backend`: Backend to use (e.g., `'sqlite'`, `'memory'`, `'redis'`, `'mongodb'`). Default is `'sqlite'`.
  * `expire_after`: Cache duration in seconds (or `None` for indefinite, `timedelta`, etc.). Default is 7 days (604800 seconds).
  * `**kwargs`: Additional arguments passed to `requests_cache.CachedSession`.

* **Example:** Use Redis cache on localhost, expiring after 1 day.
  ```python
  # Requires `pip install redis`
  # ci.setup_cache(backend='redis', expire_after=86400, host='localhost', port=6379)
  ```

## Caching Details

* Caching is enabled by default using `requests-cache` with a `sqlite` backend (`pubchem_cache.sqlite` file in the current working directory).
* Responses (including 404s) are cached to avoid repeated API calls for the same identifier.
* The default cache duration is 7 days.
* To clear the cache, simply delete the `pubchem_cache.sqlite` file (or clear based on the configured backend).
* Use `ci.setup_cache()` to customize the backend, location, or expiration time.

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to improve the library, please feel free to:

1. Open an [Issue](https://github.com/HzaCode/ChemInformant/issues) to discuss the change.
2. Fork the repository.
3. Create a new branch for your changes (`git checkout -b feature/your-feature-name`).
4. Make your changes and add tests if applicable.
5. Ensure tests pass (`pytest`).
6. Submit a [Pull Request](https://github.com/HzaCode/ChemInformant/pulls).

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

This library relies heavily on the public data provided by the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database and its PUG REST API.
