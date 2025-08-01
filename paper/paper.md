---
title: 'ChemInformant: A Robust and Workflow-Centric Python Client for High-Throughput PubChem Access'
tags:
  - python
  - pubchem
  - chemistry
  - api
  - pandas
  - cache
  - pydantic
  - cheminformatics
  - data science
  - high-throughput
authors:
  - name: Zhiang He
    orcid: 0009-0009-0171-4578
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: "2025-04-15"
bibliography: paper.bib
repository: https://github.com/HzaCode/ChemInformant
version: 2.4.0
license: MIT
---


## Summary

ChemInformant is a Python client for high-throughput, programmatic access to PubChem. It streamlines automated data retrieval by converting large, mixed-type lists of chemical identifiers directly into analysis-ready Pandas DataFrames [@Pandas]. To ensure resilience, the package integrates persistent HTTP caching, automatic rate-limiting with exponential backoff retries, and runtime data validation using Pydantic [@Pydantic]. By addressing critical limitations in existing tools, such as network instability and inefficient batch processing, ChemInformant offers up to a 48-fold performance increase, providing a more reliable and efficient component for the modern Python cheminformatics ecosystem.

## Statement of Need

Automated cheminformatics workflows require robust and efficient data access, but researchers face recurring challenges with existing PubChem clients. Network reliability is a primary concern. The PubChem API enforces dynamic rate limits, which can halt automated scripts [@PubChemUsagePolicy]. Many clients, like PubChemPy [@PubChemPy], lack built-in request throttling, retries, or persistent caching, forcing users to implement boilerplate code to handle network errors and redundant requests.

Batch processing is also often inefficient. Workflows with mixed-type identifiers (e.g., names and CIDs) require manual pre-processing. Furthermore, a single invalid identifier in a large batch can cause an entire query to fail without clear error reporting, hindering data acquisition pipelines.

ChemInformant addresses these gaps by natively integrating these critical features. Its architecture provides built-in resilience and a workflow-centric design, allowing researchers to focus on analysis rather than the low-level mechanics of data retrieval.

## State of the Field and Comparison

To contextualize `ChemInformant`, its features were compared against related tools (**Table 1**). The maintenance status of some libraries is noteworthy; for instance, PubChemPy has not had a formal release since 2017. This highlights the need for a modern, actively maintained client in the Python ecosystem.

**Table 1: Comparative analysis of key features in mainstream chemical information clients.**

| Key Feature | **ChemInformant** | PubChemPy | PubChemR | webchem | ChemSpiPy | PubChem4J |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Platform** | **Python** | Python | R | R | Python | Java |
| **Primary Database** | **PubChem** | PubChem | PubChem | Multi-DB | ChemSpider | PubChem |
| **Persistent Caching**¹ | **Yes** | No | No | No | No | N/A |
| **Rate-Limiting & Retries**² | **Yes** | No | No | Partial | No | N/A |
| **Batch Retrieval** | **Yes** | Partial | Partial | Partial | Partial | Yes |
| **Mixed Identifier Support** | **Yes** | No | No | No | No | N/A |
| **Fault Tolerance**³ | **Yes** | No | No | No | No | N/A |
| **Automatic Pagination** | **Yes** | Partial | No | No | No | N/A |
| **Runtime Type Safety** | **Yes** | No | Partial | No | No | Yes |
| **Project Activity** | **Active** | Inactive | Active | Active | Inactive | Archived |

<small>Notes: ¹ **Persistent Caching**: Stores results locally to accelerate repeated queries. ² **Rate-Limiting & Retries**: Manages API request limits and server errors for robust automation. ³ **Fault Tolerance**: Reports status per-item in batch queries, avoiding complete failure on single errors.</small>

## Performance Evaluation

To quantify `ChemInformant`'s performance, a benchmark was performed to retrieve six properties for 285 drug names. `PubChemPy` was selected as a baseline. Since `PubChemPy`'s batch interface requires CIDs, all names were first resolved to CIDs. The performance of both libraries was then timed on processing this list.

**Table 2** summarizes the performance data for the 280 successfully resolved compounds.

**Table 2: Performance benchmark results.**

| Scenario | Time (s) | Speed-up (vs. PubChemPy) |
| :--- | :--- | :--- |
| PubChemPy (batch interface) | 6.50 | 1× (Baseline) |
| **ChemInformant — Cold Cache** | **1.40** | **4.6×** |
| **ChemInformant — Warm Cache** | **0.135** | **48×** |

The initial `ChemInformant` batch query completed in **1.4 seconds**, a **4.6-fold** speed increase over `PubChemPy`. A subsequent query from the cache finished in **135 milliseconds**, a 48-fold speed-up relative to the baseline. This sub-200ms response is suitable for interactive applications. The benchmark script is available in the project repository.

## Example Usage

`ChemInformant` offers a layered API for both single lookups and batch processing.

**Convenience API Example (single lookup):**
```python
import ChemInformant as ci

# Retrieve a single property for one identifier
cas_number = ci.get_cas("ibuprofen")
# > '15687-27-1'
````

**Core API Example (batch data analysis):**
```python
# Retrieve multiple properties for a list of mixed-identifier types
df = ci.get_properties(
    identifiers=["aspirin", "caffeine", 1983], # Mix of names and a CID
    properties=["molecular_weight", "xlogp", "cas"]
)
# The returned DataFrame is formatted for direct use
print(df)
```

A detailed user manual is available in the project repository.

## Acknowledgements

The author thanks PubChem for providing open data services [@PubChem] and acknowledges the developers of the open-source libraries upon which ChemInformant is built, including requests, pandas [@Pandas], pydantic [@Pydantic], requests-cache [@RequestsCache], and pystow [@pystow].

## References

