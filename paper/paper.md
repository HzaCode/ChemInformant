---
title: 'ChemInformant: A Modern, Lightweight Python Client for PubChem with Robust Caching and Validation'
tags:
  - python
  - pubchem
  - chemistry
  - api
  - cache
  - pydantic
  - cheminformatics
  - research software
  - data validation
authors:
  - name: Zhiang HE
    orcid: 0009-0009-0171-4578
date: 15 April 2025 
bibliography: paper.bib 
repository: https://github.com/HzaCode/ChemInformant 
version: 1.1.4 
license: MIT 
doi: null 
---

# Summary

ChemInformant provides a **lightweight, highly user-friendly Pythonic interface** for accessing chemical compound data from the PubChem database [@PubChem]. Designed with simplicity and robustness in mind (`import ChemInformant as ci`), it shields researchers from the complexities of the PubChem API. Core advantages include **built-in automatic caching** via `requests-cache` [@RequestsCache] significantly enhancing performance and reproducibility, **structured data validation** using Pydantic [@Pydantic] models (`CompoundData`) ensuring data quality, **explicit handling of chemical name ambiguity** improving accuracy, and **optimized batch retrieval**. Critically, ChemInformant is built upon a minimal set of **modern, actively maintained core dependencies** (`requests` [@Requests], `requests-cache`, `Pydantic`), ensuring long-term stability and compatibility, addressing limitations found in direct API usage and offering improvements over aspects of existing tools that may rely on less modern or potentially less maintained foundations.

# Statement of Need

Accessing PubChem [@PubChem] programmatically is essential for many chemistry-related research tasks, yet direct use of the PUG REST API involves significant overhead in request handling, response parsing, error management, and data validation. This complexity can slow down research and introduce errors.

While existing libraries like PubChemPy [@PubChemPy] offer an interface to PubChem, `ChemInformant` was developed to specifically address several key limitations and provide a more modern, robust, and efficient experience tailored to common research workflows:

1.  **Dependency Modernity and Maintenance:** `ChemInformant` intentionally relies on a small set of **ubiquitous, actively developed, and well-maintained libraries** (`requests`, `requests-cache`, `Pydantic`). This contrasts with the potential risks of using tools that might depend on older libraries or libraries whose maintenance cadence may be less frequent, ensuring `ChemInformant`'s long-term stability, security, and compatibility with evolving Python environments.
2.  **Integrated Automatic Caching:** Unlike manual caching implementations or libraries lacking this feature, `ChemInformant` integrates `requests-cache` **by default**. This provides transparent, persistent caching that drastically improves performance for repeated queries and batch operations, enhances stability against network issues, and aids reproducibility – critical aspects often overlooked. The caching is also easily configurable (`ci.setup_cache()`).
3.  **Rigorous Data Validation and Structure:** `ChemInformant` uses Pydantic [@Pydantic] to define a clear `CompoundData` model. This ensures that **all retrieved data is validated at runtime**, types are enforced (e.g., weight as float), and users interact with predictable, attribute-accessible objects, not raw dictionaries. This significantly enhances code robustness and reduces errors compared to approaches lacking strict validation.
4.  **Explicit Ambiguity Handling:** A common pitfall is the ambiguity of chemical names. `ChemInformant` explicitly addresses this by raising a distinct `AmbiguousIdentifierError` with all potential CIDs when ambiguity is detected. This **prevents silent failures or arbitrary selections** and empowers the user to handle ambiguity correctly, crucial for research requiring high accuracy.
5.  **Simplicity and Ease of Use:** The API is designed to be **Pythonic and intuitive** (e.g., `ci.info()`, `ci.cas()`), significantly lowering the barrier for researchers to integrate PubChem data access into their Python scripts, Jupyter notebooks [@Jupyter], or applications without needing deep API expertise.

By focusing on these core improvements – a modern foundation, built-in caching, strong validation, clear error handling, and simplicity – `ChemInformant` aims to provide a more reliable, efficient, and developer-friendly tool for routine chemical information retrieval tasks.

# Key Functionality

`ChemInformant` delivers its core advantages through the following features:

*   **Lightweight & Pythonic Interface:** Provides an extremely simple and intuitive API. Users typically interact via the `ci` alias (`import ChemInformant as ci`), using functions like `ci.info()`, `ci.cid()`, `ci.cas()`, `ci.wgt()`, etc. This design follows common Python practices, making it easy to learn and integrate.
*   **Built-in Automatic Caching:** Leverages `requests-cache` [@RequestsCache] to automatically and transparently cache PubChem API responses. This **significantly accelerates** repeated lookups and batch processing, ensures **stability** even with network issues, and enhances **reproducibility**. Cache behavior (backend, expiration) is easily configured via `ci.setup_cache()`.
*   **Structured Validated Data (Pydantic Models):** Uses a Pydantic [@Pydantic] `CompoundData` model to structure and validate results. This **guarantees data consistency** through type checking and conversion (e.g., weight to float), promotes **code robustness** with clear object attributes, and facilitates **interoperability** with other libraries expecting structured data.
*   **Explicit Ambiguity Handling:** Addresses the critical issue of ambiguous chemical names by raising a specific `AmbiguousIdentifierError` containing all matching CIDs, rather than making a silent choice. This **enhances research accuracy** by forcing explicit handling of potential identification issues. `NotFoundError` is raised for unfound identifiers.
*   **Optimized Batch Data Retrieval:** Offers `ci.get_multiple_compounds()` for efficient processing of compound lists. This function utilizes PubChem's batch capabilities where available and integrates with the caching mechanism, **significantly improving efficiency and scalability** for high-throughput analyses.
*   **Modern & Maintained Dependencies:** Built exclusively on widely used, actively maintained libraries (`requests` [@Requests], `requests-cache` [@RequestsCache], `Pydantic` [@Pydantic]), ensuring **long-term reliability, security, and compatibility**.

# Example Usage

```python
# Recommended import alias
import ChemInformant as ci

# Optional: Configure cache (e.g., in-memory, 1-hour expiry)
# ci.setup_cache(backend='memory', expire_after=3600)

try:
    # Get full data for Aspirin by name using the alias
    aspirin_info = ci.info("Aspirin")
    print(f"Aspirin CID: {aspirin_info.cid}")
    print(f"Aspirin Formula: {aspirin_info.molecular_formula}")
    print(f"Aspirin Weight: {aspirin_info.molecular_weight:.2f}")
    print(f"Aspirin URL: {aspirin_info.pubchem_url}") # Access computed field

    # Get specific properties for Ethanol using its CID and the alias
    ethanol_cas = ci.cas(702)
    print(f"Ethanol CAS: {ethanol_cas}")

except ci.NotFoundError as e:
    print(f"Error: {e}")
except ci.AmbiguousIdentifierError as e:
    print(f"Error: {e.identifier} is ambiguous, CIDs: {e.cids}")
    # Example: Get info for the first ambiguous CID
    # first_cid_info = ci.info(e.cids[0])
    # print(f"Info for first CID ({e.cids[0]}): {first_cid_info.iupac_name}")

# Batch lookup using the alias
results = ci.get_multiple_compounds(["Water", 2244, "NonExistent", "glucose"]) # 'glucose' might be ambiguous
print(results)

```

More detailed examples can be found in the project's README file [@ChemInformantRepo].
# Acknowledgements
We acknowledge the PubChem database [@PubChem] as the primary source of data used by this software. This work utilizes the open-source libraries requests [@Requests], requests-cache [@RequestsCache], and Pydantic [@Pydantic].