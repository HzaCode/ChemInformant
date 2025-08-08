
# ChemInformant <img src="https://raw.githubusercontent.com/HzaCode/ChemInformant/main/images/logo.png" align="right" width="120px" />


<p style="margin:12px 0; text-align:left;">
  <a href="https://pepy.tech/project/cheminformant">
    <img
      src="https://img.shields.io/pepy/dt/cheminformant?style=flat-square&color=306998&label=Downloads&logo=python"
      alt="Total Downloads"
      height="70">
  </a>
</p>



<a href="https://joss.theoj.org/papers/b263ab8f865610c7c7a7f981035f78f7"><img src="https://joss.theoj.org/papers/b263ab8f865610c7c7a7f981035f78f7/status.svg"></a>
[![PyPI version](https://img.shields.io/pypi/v/ChemInformant.svg)](https://pypi.org/project/ChemInformant/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.8-blue.svg)](https://pypi.org/project/ChemInformant/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/HzaCode/ChemInformant/tests.yml?label=Build)](https://github.com/HzaCode/ChemInformant/actions/workflows/tests.yml) 
![coverage](https://cdn.jsdelivr.net/gh/HzaCode/ChemInformant@gh-pages/coverage.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - License](https://img.shields.io/pypi/l/ChemInformant.svg)](https://github.com/HzaCode/ChemInformant/blob/main/LICENSE.md)
[![Docs](https://img.shields.io/badge/Docs-Read_Online-blue?style=flat-square&logo=book&logoColor=white)](https://hezhiang.com/ChemInformant)[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ba35e3e2f5224858bcaeb8f9c4ee2838)](https://app.codacy.com/gh/HzaCode/ChemInformant/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16623785.svg)](https://doi.org/10.5281/zenodo.16623785)





**ChemInformant** is a robust data acquisition engine for the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database, engineered for the modern scientific workflow. It intelligently manages network requests, performs rigorous runtime data validation, and delivers analysis-ready results, providing a dependable foundation for any computational chemistry project in Python.

---

### Key Features

*   **Analysis-Ready Pandas/SQL Output:** The core API (`get_properties`) returns either a clean Pandas DataFrame or a direct SQL output, eliminating data wrangling boilerplate and enabling immediate integration with both the Python data science ecosystem and modern database workflows.

*   **Automated Network Reliability:** Ensures your workflows run flawlessly with built-in persistent caching, smart rate-limiting, and automatic retries. It also transparently handles API pagination (`ListKey`) for large-scale queries, delivering complete result sets without any manual intervention.

*   **Flexible & Fault-Tolerant Input:** Natively accepts mixed lists of identifiers (names, CIDs, SMILES) and intelligently handles any invalid inputs by flagging them with a clear status in the output, ensuring a single bad entry never fails an entire batch operation.

*   **A Dual API for Simplicity and Power:** Offers a clear `get_<property>()` convenience layer for quick lookups, backed by a powerful `get_properties` engine for high-performance batch operations.

*   **Guaranteed Data Integrity:** Employs Pydantic v2 models for rigorous, runtime data validation when using the object-based API, preventing malformed or unexpected data from corrupting your analysis pipeline.

*   **Terminal-Ready CLI Tools:** Includes `chemfetch` and `chemdraw` for rapid data retrieval and 2D structure visualization directly from your terminal, perfect for quick lookups without writing a script.

*   **Modern and Actively Maintained:** Built on a contemporary tech stack for long-term consistency and compatibility, providing a reliable alternative to older or less frequently updated libraries.
  
---

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

# 4. Save the results to an SQL database
ci.df_to_sql(df, "sqlite:///chem_data.db", "results", if_exists="replace")

# 5. Analyze your results!
print(df)


```

**Output:**

```
  input_identifier   cid status  molecular_weight  xlogp       cas
0          aspirin  2244     OK            180.16    1.2   50-78-2
1         caffeine  2519     OK            194.19   -0.1   58-08-2
2             1983  1983     OK            151.16    0.5  103-90-2
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
| `get_isomeric_smiles(id)`  | Isomeric SMILES with Isomeric→SMILES fallback *(str)* |
| `get_xlogp(id)`            | XLogP (calculated hydrophobicity) *(float)*   |
| `get_synonyms(id)`         | List of synonyms *(List[str])*                |
| `get_compound(id)`         | Full, validated **`Compound`** object (Pydantic v2 model) |

*Note: This table shows key convenience functions for demonstration. ChemInformant provides **22 convenience functions** in total, covering molecular descriptors, mass properties, stereochemistry, and more.*

*All functions accept a **CID, name, or SMILES** and return `None`/`[]` on failure.*

</details>



ChemInformant also includes handy command-line tools for quick lookups directly from your terminal:

*   **`chemfetch`**: Fetches properties for one or more compounds.
    ```bash
    chemfetch aspirin --props "cas,molecular_weight,iupac_name"
    ```

*   **`chemdraw`**: Renders the 2D structure of a compound.
    ```bash
    chemdraw aspirin
    ```
---
### Documentation & Examples

For a deep dive, please see our detailed guides:

*   **➡️ Online Documentation:** The **[official documentation site](https://hezhiang.com/ChemInformant)** contains complete API references, guides, and usage examples. **This is the most comprehensive resource.**
*   **➡️ Interactive User Manual:** Our [**Jupyter Notebook Tutorial**](examples/ChemInformant_User_Manual_v1.0.ipynb) provides a complete, end-to-end walkthrough. This is the best place to start for a hands-on experience.
*   **➡️ Performance Benchmarks:** You can review and run our [**Benchmark Script**](./benchmark.py) to see the performance advantages of batching and caching.

---

### Why ChemInformant?

ChemInformant's core mission is to serve as a high-performance data backbone for the Python cheminformatics ecosystem. By delivering clean, validated, and analysis-ready Pandas DataFrames, it enables researchers to effortlessly pipe PubChem data into powerful toolkits like RDKit, Scikit-learn, or custom machine learning models, transforming multi-step data acquisition and wrangling tasks into single, elegant lines of code.

A detailed comparison with other existing tools is provided in our [JOSS paper](https://github.com/HzaCode/ChemInformant/blob/main/paper/paper.md).

### Contributing

Contributions are welcome! For guidelines on how to get started, please read our [contributing guide](https://github.com/HzaCode/ChemInformant/blob/main/CONTRIBUTING.md). You can [open an issue](https://github.com/HzaCode/ChemInformant/issues) to report bugs or suggest features, or [submit a pull request](https://github.com/HzaCode/ChemInformant/pulls) to contribute code.
### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
### Citation

If you use **ChemInformant** in your research, please cite the software using the following format:

> **Software**: He, Z. *ChemInformant* [Software], version 2.4.0, Zenodo, https://doi.org/10.5281/zenodo.16623785

