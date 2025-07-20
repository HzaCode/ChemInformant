# ChemInformant <img src="https://raw.githubusercontent.com/HzaCode/ChemInformant/main/images/logo.png" align="right" width="120px" />



[![Total Downloads](https://img.shields.io/pepy/dt/cheminformant?label=Downloads&color=blue)](https://pepy.tech/project/cheminformant)

[![Status: Revisions in Progress](https://img.shields.io/badge/Status-Revisions%20in%20Progress-orange.svg?style=flat-square)](#) [![PyPI version](https://img.shields.io/pypi/v/ChemInformant.svg)](https://pypi.org/project/ChemInformant/)[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-blue.svg)](https://pypi.org/project/ChemInformant/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/HzaCode/ChemInformant/tests.yml?label=Build)](https://github.com/HzaCode/ChemInformant/actions/workflows/tests.yml) 
[![codecov](https://codecov.io/gh/HzaCode/ChemInformant/graph/badge.svg)](https://codecov.io/gh/HzaCode/ChemInformant)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - License](https://img.shields.io/pypi/l/ChemInformant.svg)](https://github.com/HzaCode/ChemInformant/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/Docs-Read_Online-blue?style=flat-square&logo=book&logoColor=white)](https://hezhiang.com/ChemInformant/usage.html)


**ChemInformant** is a modern, workflow-centric **Python client** for the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database. It's designed to feel native and intuitive for researchers and data scientists working within the **Python data science ecosystem.

It's built to be robust by default, with built-in request caching, smart rate limiting, and automatic retries to handle real-world network conditions.

---

### Key Features

*   **Analysis-Ready Pandas Output:** The core API (`get_properties`) returns a clean Pandas DataFrame, eliminating data wrangling boilerplate and enabling immediate integration with the Python data science ecosystem.
*   **Zero-Configuration Robustness:** Built-in, persistent caching, smart rate-limiting, and automatic retries for server errors are enabled by default to ensure your workflows run reliably.
*   **A Dual API for Simplicity and Power:** Offers a clear `get_<property>()` convenience layer for quick lookups, backed by a powerful `get_properties` engine for high-performance batch operations.
*   **Effortless Large-Scale Queries:** Transparently handles PubChem's `ListKey`-based pagination in the background, ensuring you retrieve complete result sets from large queries without manual intervention.
*   **Guaranteed Data Integrity:** Employs Pydantic v2 models for rigorous, runtime data validation, preventing malformed or unexpected data from corrupting your analysis pipeline.
*   **Modern and Actively Maintained:** Built on a contemporary tech stack for long-term **consistency**  and compatibility, providing a reliable alternative to older or less frequently updated libraries.
### Installation

Install the library from PyPI:

```bash
pip install ChemInformant
```

To include plotting capabilities for use with the tutorial, install the `[plot]` extra:
```bash
pip install "ChemInformant[plot]"
```

---

### Quick Start

Retrieve multiple properties for multiple compounds, directly into a Pandas DataFrame, in a single function call:

```python
import ChemInformant as ci

# 1. Define your identifiers
identifiers = ["aspirin", "caffeine", 1983] # 1983 is paracetamol's CID

# 2. Specify the properties you need
properties = ["molecular_weight", "xlogp", "cas"]

# 3. Call the core function
df = ci.get_properties(identifiers, properties)

# 4. Analyze your results!
print(df)
```

**Output:**

```
  input_identifier     cid status  molecular_weight  xlogp       cas
0          aspirin  2244.0     OK            180.16   1.20   50-78-2
1         caffeine  2519.0     OK            194.19  -0.07   58-08-2
2             1983  1983.0     OK            151.16   0.51  103-90-2
```

<details>
<summary><b>➡️ Click to see Convenience API Cheatsheet</b></summary>
<br>

| Function                   | Description                                   |
|----------------------------|-----------------------------------------------|
| `get_weight(id)`           | Molecular weight *(float)*                    |
| `get_formula(id)`          | Molecular formula *(str)*                     |
| `get_cas(id)`              | CAS Registry Number *(str)*                   |
| `get_iupac_name(id)`       | IUPAC name *(str)*                            |
| `get_canonical_smiles(id)` | Canonical SMILES with Canonical→Connectivity fallback *(str)* |
| `get_isomeric_smiles(id)`  | Isomeric SMILES *(str)*                       |
| `get_xlogp(id)`            | XLogP (calculated hydrophobicity) *(float)*   |
| `get_synonyms(id)`         | List of synonyms *(List[str])*                |
| `get_compound(id)`         | Full, validated **`Compound`** object (Pydantic v2 model) |


*All functions accept a **CID, name, or SMILES** and return `None`/`[]` on failure.*

</details>

---

### Documentation & Examples

This quick start only scratches the surface. For a deep dive, please see our detailed guides:

*   **➡️ Interactive User Manual:** Our [**Jupyter Notebook Tutorial**](examples/ChemInformant_User_Manual_v1.0.ipynb)provides a complete, end-to-end walkthrough. **This is the best place to start.**
*   **➡️ Performance Benchmarks:** You can review and run our [**Benchmark Script**](./benchmark.py) to see the performance advantages of batching and caching.

---

### Why ChemInformant?

ChemInformant's core mission is to serve as a high-performance data backbone for the Python cheminformatics ecosystem. By delivering clean, validated, and analysis-ready Pandas DataFrames, it enables researchers to effortlessly pipe PubChem data into powerful toolkits like RDKit, Scikit-learn, or custom machine learning models, transforming multi-step data acquisition and wrangling tasks into single, elegant lines of code.

A detailed comparison with other existing tools is provided in our JOSS paper.

### Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
