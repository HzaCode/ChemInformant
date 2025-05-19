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
  - name: Zhiang He
    orcid: 0009-0009-0171-4578
affiliation: 
date: 15 April 2025
bibliography: paper.bib # Assuming your .bib file is named paper.bib
repository: https://github.com/HzaCode/ChemInformant
version: 1.1.5 
license: MIT
doi:
---

## Summary

ChemInformant provides a **lightweight, highly user-friendly Pythonic interface** for accessing chemical compound data from the PubChem database [@PubChem; @Kim2016NAR]. Designed with simplicity and robustness in mind (`import ChemInformant as ci`), it shields researchers from the complexities of the PubChem API. Core advantages include **built-in automatic caching** via `requests-cache` [@RequestsCache] significantly enhancing performance and reproducibility, **structured data validation** using Pydantic [@Pydantic] models (`CompoundData`) ensuring data quality, **explicit handling of chemical name ambiguity** improving accuracy, and **optimized batch retrieval**. Critically, ChemInformant is built upon a minimal set of **modern, actively maintained core dependencies** (`requests` [@Requests], `requests-cache`, `Pydantic`), ensuring long-term stability and compatibility. This addresses limitations found in direct API usage and offers improvements over aspects of existing tools that may rely on less modern or potentially less maintained foundations. ChemInformant aims to be a reliable and efficient tool for routine chemical information retrieval.

## Statement of Need

Accessing PubChem [@PubChem] programmatically is essential for many chemistry-related research tasks, yet direct use of the PUG REST API [@Kim2018JCheminform; @Kim2018PUGREST] involves significant overhead in request handling, response parsing, error management, and data validation. This complexity can slow down research and introduce errors.

While existing libraries like PubChemPy [@PubChemPy] offer an interface to PubChem, `ChemInformant` was developed to specifically address several key limitations and provide a more modern, robust, and efficient experience tailored to common research workflows:

1.  **Dependency Modernity and Maintenance:** `ChemInformant` intentionally relies on a small set of ubiquitous, actively developed, and well-maintained libraries (`requests` [@Requests], `requests-cache` [@RequestsCache], `Pydantic` [@Pydantic]). This ensures long-term stability, security, and compatibility with evolving Python [@Python] environments.
2.  **Integrated Automatic Caching:** `ChemInformant` integrates `requests-cache` **by default**, providing transparent, persistent caching that drastically improves performance for repeated queries and batch operations, enhances stability against network issues, and aids reproducibility. The caching is also easily configurable (`ci.setup_cache()`).
3.  **Rigorous Data Validation and Structure:** `ChemInformant` uses Pydantic to define a clear `CompoundData` model, ensuring retrieved data is validated at runtime, types are enforced, and users interact with predictable objects.
4.  **Explicit Ambiguity Handling:** `ChemInformant` explicitly addresses chemical name ambiguity by raising a distinct `AmbiguousIdentifierError` with all potential CIDs, preventing silent failures or arbitrary selections.
5.  **Simplicity and Ease of Use:** The API is designed to be Pythonic and intuitive (e.g., `ci.info()`, `ci.cas()`), lowering the barrier for researchers to integrate PubChem data access into Python scripts or Jupyter notebooks [@Jupyter].

By focusing on these core improvements, `ChemInformant` aims to provide a more reliable, efficient, and developer-friendly tool for routine chemical information retrieval tasks. The target users are cheminformatics researchers, drug discovery scientists, computational chemists, data scientists, and educators.

## Key Functionality and Architecture

ChemInformant delivers its advantages through a modular architecture (Figure 1) and key features:

*   **Lightweight & Pythonic Interface:** Simple API via `ci` alias (e.g., `ci.info()`, `ci.cid()`).
*   **Built-in Automatic Caching:** Leverages `requests-cache` [@RequestsCache] for transparent caching (default: SQLite, 7-day expiry, caches 404s), configurable via `ci.setup_cache()`.
*   **Structured Validated Data:** Uses a Pydantic [@Pydantic] `CompoundData` model for data consistency and robustness.
*   **Explicit Ambiguity Handling:** Raises `AmbiguousIdentifierError` for ambiguous names, `NotFoundError` for unfound identifiers.
*   **Optimized Batch Data Retrieval:** `ci.get_multiple_compounds()` for efficient processing of compound lists.
*   **Modern Dependencies:** Built on `requests` [@Requests], `requests-cache`, `Pydantic`.


![ChemInformant Architecture Diagram](cheminformant_flowchart.png){#fig:architecture_flowchart}

Figure 1: ChemInformant architecture. Inputs (user input, PubChem API, dependencies) flow into the central component. ChemInformant utilizes key features (smart caching, robust validation, proactive disambiguation, optimized batch processing, concise API) to produce validated outputs (`CompoundData` objects or specific exceptions), suitable for downstream tools and analysis.
## Example Usage

The following example demonstrates basic usage of ChemInformant:

```python
# Recommended import alias
import ChemInformant as ci

# Optional: Configure cache (e.g., in-memory, 1-hour expiry)
# ci.setup_cache(backend='memory', expire_after=3600)

# Retrieve basic information about Aspirin (by name or CID)
compound = ci.info("Aspirin")
print("Name:", compound.common_name)
print("Formula:", compound.molecular_formula)
print("Weight:", compound.molecular_weight)
print("PubChem URL:", compound.pubchem_url)

# Display 2D structure (requires Pillow and matplotlib)
ci.fig(compound.cid)

# Retrieve CAS number for Ethanol (CID = 702)
ethanol_cas = ci.cas(702)
print("Ethanol CAS:", ethanol_cas)

# Batch retrieval: mix of names and CIDs
ids = ["Water", 2244, "NonExistent", "glucose"]
results = ci.get_multiple_compounds(ids)

print("\nBatch Results:")
for ident, result in results.items():
    if isinstance(result, ci.CompoundData):
        print(ident, "→", result.molecular_formula)
    else:
        print(ident, "→", type(result).__name__)

```

**Table 1. Feature comparison: ChemInformant (CI) vs. PubChemPy (PCP v1.0.4)** {#tbl:features}
| Feature                     | ChemInformant (CI)                                                                                                                                                               | PubChemPy (PCP v1.0.4)                                                                                                                                                                |
| :-------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Persistent HTTP Cache**   | Built-in `requests-cache`, supporting SQLite/memory/Redis backends. Subsequent requests for cached data can achieve near-zero network traffic in repetitive analysis scenarios, significantly improving efficiency.| No global caching mechanism; each batch request re-accesses the network, resulting in an inability to leverage caching for acceleration during repeated retrievals, and fixed network overhead. |
| **Runtime Data Validation** | Employs Pydantic `CompoundData` model for immediate validation of field types and missing data, actively raising errors.                                                               | Returns native Python objects (e.g., dictionaries) with no built-in mandatory validation mechanism; users are responsible for their own data checks.                                         |
| **Chemical Name Disambiguation** | Automatically raises an `AmbiguousIdentifierError` exception; the exception object (`e`) includes an `e.cids` attribute listing all candidate CIDs, allowing developers to select one to proceed (e.g., `ci.info(e.cids[0])`). Enforces handling of ambiguity to prevent misuse of compounds. | Directly returns a list of results without erroring on ambiguity; developers must manually check the list length (e.g., `len(hits)`) and review the results, otherwise, it defaults to using the first item in the list, which can easily lead to incorrect selections. |
| **Batch Retrieval**         | Single call to `ci.get_multiple_compounds(ids)`: supports mixed ID types, automatically handles classification, pagination (≤ 200 entries/batch), and rate limiting (≤ 5 reqs/sec); error entries are encapsulated as exception objects, while valid entries return complete `CompoundData`. | Requires users to manually split IDs by namespace, then loop through `get_properties` / `get_compounds`, and self-manage request rates (e.g., via `sleep`); if batch size exceeds limits or URL construction is incorrect, the entire batch request fails. |
| **2-D Structure Drawing**   | Provides `ci.fig(cid)` method for single-line rendering via Pillow and Matplotlib; supports inline display in Jupyter Notebooks.                                                       | No built-in drawing functionality; only returns image URLs (PNG/SVG format), requiring users to manually download them for display.                                                              |
| **Core Dependencies & Maintenance** | Core dependencies include `requests` 2.x, `requests-cache` 1.x, `pydantic` 2.x, all actively maintained versions; the CI package itself is also under continuous development and updates . | Core dependency is primarily `requests`; PCP's latest stable version was released in 2017, with low subsequent maintenance activity.                                                              |

Together, these comparative advantages show that ChemInformant is not just a convenient alternative but an essential, modern choice for routine cheminformatics workflows—delivering measurable gains in efficiency, reliability, and data integrity.

## Acknowledgement

We acknowledge the PubChem database [@PubChem] as the primary data source. This work utilizes a series of open-source Python libraries for tasks including data requests, caching, validation, as well as optional image processing and data visualization.

