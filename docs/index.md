

<img src="assets/logo.png" alt="ChemInformant Logo" align="right" width="180" />

# <!-- an empty title -->

## A Robust and Workflow-Centric Python Client for High-Throughput PubChem Access

**ChemInformant** is a modern Python client engineered for high-throughput and automated PubChem data tasks. It is designed not merely as an API wrapper, but as a reliable data infrastructure component for the Python cheminformatics ecosystem.

Its architecture systematically addresses key limitations of existing tools in network reliability, batch processing flexibility, and long-term maintainability, enabling the direct conversion of diverse chemical identifiers into analysis-ready `pandas` DataFrames.

---

### A Solution Engineered for Scale and Reliability

ChemInformant was created to solve the critical challenges faced in modern, automated chemical and life sciences research.

| Challenge Addressed            | ChemInformant's Architectural Solution                                                                                                                                     |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Network Unreliability**      | Built-in, zero-configuration **automatic rate-limiting and exponential backoff retries**. Scripts are resilient to PubChem's dynamic load (`503` errors) and network hiccups. |
| **Inefficient Data Retrieval** | A powerful **persistent caching** engine (`requests-cache`) delivers up to a **50x speed-up** on repeated queries, enabling interactive analysis and reducing API quota usage. |
| **Inflexible Batch Processing**  | **Native support for mixed-type identifiers** (names, CIDs, SMILES) and a fault-tolerant engine that processes valid entries while gracefully reporting errors for invalid ones. |
| **Workflow Friction**          | Directly outputs structured `pandas.DataFrame` objects with detailed status metadata, eliminating the need for manual data cleaning and wrangling before analysis.         |
| **Data & Code Integrity**      | Leverages **Pydantic** for runtime data validation, ensuring that the data structures you receive are always consistent and correct.                                       |


### From Raw Identifiers to Insight

The core philosophy is to minimize the steps between a list of identifiers and meaningful analysis.

```python
import ChemInformant as ci

# A raw list of mixed-type identifiers, common in real-world tasks
identifiers = ["aspirin", "caffeine", 1983, "invalid_name"]

# A single, robust function call to retrieve multiple properties
df = ci.get_properties(
    identifiers=identifiers,
    properties=["molecular_weight", "xlogp", "cas", "iupac_name"]
)

# The result is a structured, analysis-ready DataFrame
print(df.head())
```

**Resulting DataFrame:**

```
     input_identifier    cid                  status  molecular_weight  xlogp      cas                       iupac_name
0             aspirin   2244                      OK           180.160    1.2  50-78-2  2-(acetyloxy)benzoic acid
1            caffeine   2519                      OK           194.190   -0.0  58-08-2   1,3,7-trimethylpurine-2,6-dione
2                1983   1983                      OK           151.160    1.2  50-00-0                      formaldehyde
3        invalid_name   None           NotFoundError              NaN    NaN     None                              None
```

### Documentation Structure

-   **[Usage Guide](usage.md)**: A comprehensive guide covering installation, configuration, and detailed examples of all core functionalities. This is the recommended starting point.

-   **[Jupyter Tutorial](notebook.md)**: A hands-on walkthrough of a practical analysis workflow, demonstrating how to leverage ChemInformant for data-driven research.

-   **[API Reference](api.md)**: The definitive, auto-generated technical reference for every public class, function, and method available in the library.

Ready to integrate a more robust data backbone into your workflow? Start with the **[Usage Guide](usage.md)**.
