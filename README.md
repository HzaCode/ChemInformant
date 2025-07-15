# ChemInformant <img src="https://raw.githubusercontent.com/HzaCode/ChemInformant/joss-review-response/images/logo.png" align="right" width="120px" />

[![Status: Revisions in Progress](https://img.shields.io/badge/Status-Revisions%20in%20Progress-orange.svg?style=flat-square)](#)

**ChemInformant** is a modern, workflow-centric **Python client** for the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database. It's designed to feel native and intuitive for researchers and data scientists working within the **Python data science ecosystem (e.g., Pandas, Jupyter)**.

It's built to be robust by default, with built-in request caching, smart rate limiting, and automatic retries to handle real-world network conditions.

---

### Key Features

*   **Native Pandas Output:** Core API returns a clean, ready-to-analyze **Pandas DataFrame**.
*   **Robust by Default:** Built-in caching, rate-limiting, and retries are enabled with zero configuration.
*   **Intuitive Layered API:** Offers both simple `get_<property>()` functions for quick lookups and a powerful `get_properties` engine for batch operations.
*   **Automated Pagination:** Transparently handles PubChem's `ListKey`-based pagination for large queries.
*   **Type-Safe & Validated:** Employs Pydantic v2 models to ensure the data you receive is structured and type-checked.
*   **Modern & Maintained:** Built on an actively maintained tech stack for long-term stability.

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

*   **➡️ Interactive User Manual:** Our [**Jupyter Notebook Tutorial**](./ChemInformant_User_Manual.ipynb) provides a complete, end-to-end walkthrough. **This is the best place to start.**
*   **➡️ Performance Benchmarks:** You can review and run our [**Benchmark Script**](./benchmark.py) to see the performance advantages of batching and caching.

---

### Why ChemInformant?

ChemInformant's core mission is to serve as a high-performance data backbone for the Python cheminformatics ecosystem. By delivering clean, validated, and analysis-ready Pandas DataFrames, it enables researchers to effortlessly pipe PubChem data into powerful toolkits like RDKit, Scikit-learn, or custom machine learning models, transforming multi-step data acquisition and wrangling tasks into single, elegant lines of code.

A detailed comparison with other existing tools is provided in our JOSS paper.

### Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
