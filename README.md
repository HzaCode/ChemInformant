# ChemInformant <img src="https://github.com/HzaCode/ChemInformant/blob/joss-review-response/images/logo.jpg?raw=true" align="right" width="120px" />


[![Status: Revisions in Progress](https://img.shields.io/badge/Status-Revisions%20in%20Progress-orange.svg?style=flat-square)](#)


**ChemInformant** is a modern, workflow-centric **Python client** for the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database. It's designed to feel native and intuitive for researchers and data scientists working within the **Python data science ecosystem (e.g., Pandas, Jupyter)**.

It's built to be robust by default, with built-in request caching, smart rate limiting, and automatic retries to handle real-world network conditions.

---

### Key Features

*   **Workflow-First Design (Native Pandas Output):** The core API (`get_properties`) directly returns a clean **Pandas DataFrame**, eliminating boilerplate code and allowing for immediate integration with other data science libraries.

*   **Robust by Default (Caching, Rate-Limiting & Retries):**
    *   **Transparent Caching:** Built-in, persistent caching significantly accelerates repetitive queries.
    *   **Smart Rate-Limiting & Retries:** Automatically adheres to PubChem's usage policies and gracefully handles temporary server issues with an exponential backoff mechanism.

*   **Intuitive Layered API:**
    *   A **convenience layer** of `get_<property>()` functions for quick, simple lookups.
    *   A **powerful engine layer** (`get_properties`) for complex, performance-critical batch operations.

*   **Automated Pagination:** Transparently handles PubChem's `ListKey`-based pagination, effortlessly retrieving complete result sets from large queries without manual intervention.

*   **Type-Safe and Validated:** Employs Pydantic v2 models (`Compound`) to ensure the data you receive is structured and type-checked, preventing common errors downstream.

*   **Modern Tech Stack & Maintenance:** Built on a minimal set of **actively maintained libraries** (like `requests-cache` and `Pydantic v2`), ensuring long-term stability and compatibility, in contrast to older, less frequently updated tools.

### Installation

Install the library from PyPI:

```bash
pip install ChemInformant
```

To include plotting capabilities for use with the tutorial, install the `[plot]` extra:
```bash
pip install "ChemInformant[plot]"
```

### Quick Start

Retrieve multiple properties for multiple compounds, directly into a Pandas DataFrame, in a single function call:

```python
import ChemInformant as ci
import pandas as pd

# 1. Define your identifiers
identifiers = ["aspirin", "caffeine", "paracetamol", "NonExistentCompound"]

# 2. Specify the properties you need
properties = ["molecular_weight", "xlogp", "cas"]

# 3. Call the core function
df = ci.get_properties(identifiers, properties)

# 4. Analyze your results!
print(df)
```

**Output:**

```
      input_identifier      cid        status  molecular_weight  xlogp        cas
0              aspirin   2244.0            OK           180.159   1.28    50-78-2
1             caffeine   2519.0            OK           194.190   -0.01  58-08-2
2          paracetamol   1983.0            OK           151.163   0.51  103-90-2
3  NonExistentCompound      NaN   NotFoundError              NaN    NaN       NaN
```

### Documentation & Examples

This quick start only scratches the surface. To learn more, please see our detailed guides:

*   **➡️ Interactive User Manual:** Our [**Jupyter Notebook Tutorial**](./ChemInformant_User_Manual_v2.1.ipynb) provides a complete, end-to-end walkthrough. **This is the best place to start.**
*   **➡️ Performance Benchmarks:** You can review and run our [**Benchmark Script**](./benchmark.py) to see the performance advantages of batching and caching.
*   **➡️ Full API Reference:** *(Coming soon)*

---

### Why ChemInformant?

ChemInformant's core mission is to serve as a high-performance data backbone for the Python cheminformatics ecosystem. It is engineered to be the most efficient upstream data source for subsequent analysis. By delivering clean, validated, and analysis-ready Pandas DataFrames, ChemInformant enables researchers to effortlessly pipe PubChem data into powerful toolkits like RDKit, Scikit-learn, or custom machine learning models, transforming multi-step data acquisition and wrangling tasks into single, elegant lines of code.

A detailed comparison with other existing tools is provided in our JOSS paper.


### Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
