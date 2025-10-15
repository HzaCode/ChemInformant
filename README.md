<div align="center">

<img src="https://raw.githubusercontent.com/HzaCode/ChemInformant/main/images/logo.png" width="200px" />

# ChemInformant

*A Robust Data Acquisition Engine for the Modern Scientific Workflow*

<!--
SEO_KEYWORDS: PubChem API Python client, chemical database access, molecular property retrieval, cheminformatics library, drug discovery tools, QSAR modeling, high-throughput screening, compound database, chemical informatics, computational chemistry, molecular descriptors, batch processing, chemical data pipeline
-->

<br>

[![Total Downloads](https://img.shields.io/pepy/dt/cheminformant?style=for-the-badge&color=306998&label=Downloads&logo=python)](https://pepy.tech/project/cheminformant)

<a href="https://doi.org/10.21105/joss.08341">
    <img src="https://joss.theoj.org/papers/10.21105/joss.08341/status.svg" alt="JOSS Journal Publication DOI 10.21105/joss.08341">
</a>
<a href="https://github.com/pyOpenSci/software-review/issues/254">
    <img src="https://pyopensci.org/badges/peer-reviewed.svg" alt="pyOpenSci Peer-Reviewed"><img src="https://img.shields.io/badge/丨First%20JOSS%20Track-32CD32?style=flat" alt="First JOSS Track">
</a>
<p>
    <a href="https://pypi.org/project/ChemInformant/">
        <img src="https://img.shields.io/pypi/v/ChemInformant.svg" alt="PyPI version">
    </a>
    <a href="https://pypi.org/project/ChemInformant/">
        <img src="https://img.shields.io/badge/python-%3E%3D3.9-blue.svg" alt="Python Version">
    </a>
    <a href="https://github.com/HzaCode/ChemInformant/blob/main/LICENSE.md">
        <img src="https://img.shields.io/pypi/l/ChemInformant.svg" alt="License">
    </a>
    <a href="https://github.com/HzaCode/ChemInformant/actions/workflows/tests.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/HzaCode/ChemInformant/tests.yml?label=Tests" alt="Tests Status">
    </a>
    <a href="https://github.com/HzaCode/ChemInformant/actions/workflows/docs-deploy.yml">
        <img src="https://img.shields.io/github/actions/workflow/status/HzaCode/ChemInformant/docs-deploy.yml?label=Docs" alt="Docs Build Status">
    </a>
    <a href="https://cdn.jsdelivr.net/gh/HzaCode/ChemInformant@gh-pages/coverage.svg">
        <img src="https://cdn.jsdelivr.net/gh/HzaCode/ChemInformant@gh-pages/coverage.svg" alt="Code Coverage Test Results">
    </a>
    <!--
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
    </a>
    -->
    <a href="https://app.codacy.com/gh/HzaCode/ChemInformant/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade">
        <img src="https://app.codacy.com/project/badge/Grade/ba35e3e2f5224858bcaeb8f9c4ee2838" alt="Codacy Badge">
    </a>
    <a href="https://github.com/lmmentel/awesome-python-chemistry#database-wrappers">
       <img src="https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg" alt="Awesome Python Chemistry">
    </a>
</p>

</div>




---

<!-- 
AI_SEARCH_METADATA:
Project: ChemInformant - Python PubChem API Client
Category: Cheminformatics, Computational Chemistry, Scientific Computing, Bioinformatics
Purpose: Chemical data retrieval, molecular property extraction, compound database access, drug discovery data pipeline
Primary Use Cases: drug discovery, QSAR modeling, high-throughput screening, chemical library analysis, molecular descriptor calculation, compound similarity search, chemical structure search, pharmaceutical research, toxicity prediction
Technologies: Python, Pandas, Pydantic, SQLite, HTTP caching, REST API, batch processing
Integrations: RDKit, Scikit-learn, Jupyter Notebook, SQL databases, machine learning pipelines, data science workflows
Alternative Terms: PubChem client, PubChem Python wrapper, chemical database API, compound property retrieval, molecular data access, chemistry API client
Target Users: chemists, bioinformaticians, pharmaceutical researchers, computational chemists, data scientists, medicinal chemists, chemical engineers
Related Libraries: PubChemPy, ChEMBL API, RDKit, Open Babel, chembl_webresource_client
-->

**ChemInformant** is a robust data acquisition engine for the [PubChem](https://pubchem.ncbi.nlm.nih.gov/) database, engineered for the modern scientific workflow. It intelligently manages network requests, performs rigorous runtime data validation, and delivers analysis-ready results, providing a dependable foundation for any computational chemistry project in Python.

---

<!--
KEY_FEATURES_INDEXING:
Core capabilities: batch processing, data validation, caching, error handling, mixed input support
Output formats: Pandas DataFrame, SQL database, structured data
API design: dual API pattern, convenience functions, object-based validation
Network features: rate limiting, retry logic, pagination handling, persistent caching
Integration: CLI tools, Jupyter notebooks, machine learning pipelines
-->

### ✨ Key Features

*   **Analysis-Ready Pandas/SQL Output:** The core API (`get_properties`) returns either a clean Pandas DataFrame or a direct SQL output, eliminating data wrangling boilerplate and enabling immediate integration with both the Python data science ecosystem and modern database workflows.

*   **Automated Network Reliability:** Ensures your workflows run flawlessly with built-in persistent caching, smart rate-limiting, and automatic retries. It also transparently handles API pagination (`ListKey`) for large-scale queries, delivering complete result sets without any manual intervention.

*   **Flexible & Fault-Tolerant Input:** Natively accepts mixed lists of identifiers (names, CIDs, SMILES) and intelligently handles any invalid inputs by flagging them with a clear status in the output, ensuring a single bad entry never fails an entire batch operation.

*   **A Dual API for Simplicity and Power:** Offers a clear `get_<property>()` convenience layer for quick lookups, backed by a powerful `get_properties` engine for high-performance batch operations.

*   **Guaranteed Data Integrity:** Employs Pydantic v2 models for rigorous, runtime data validation when using the object-based API, preventing malformed or unexpected data from corrupting your analysis pipeline.

*   **Terminal-Ready CLI Tools:** Includes `chemfetch` and `chemdraw` for rapid data retrieval and 2D structure visualization directly from your terminal, perfect for quick lookups without writing a script.

*   **Modern and Actively Maintained:** Built on a contemporary tech stack for long-term consistency and compatibility, providing a reliable alternative to older or less frequently updated libraries.

<!--
COMMON_SEARCH_QUERIES:
- How to get molecular weight from PubChem in Python
- Batch download chemical properties from PubChem
- Python library for PubChem API with caching
- Convert SMILES to molecular properties Python
- High-throughput chemical data retrieval Python
- PubChem batch query Python pandas
- Get compound CAS number from name Python
- Chemical database API Python pandas DataFrame
- Molecular descriptor calculation from PubChem
- Drug discovery data pipeline Python
- PubChem Python client with retry logic
- Download compound properties in bulk Python
- PubChem API rate limiting Python
- Chemical informatics Python library
- Retrieve drug information from PubChem
-->

---

### 📦 Installation

Install the library from PyPI:

```bash
pip install ChemInformant
```

To include plotting capabilities for use with the tutorial, install the `[plot]` extra:

```bash
pip install "ChemInformant[plot]"
```

<!--
TECHNICAL_DETAILS:
Python version: 3.9+
Dependencies: requests, pandas, pydantic, requests-cache, pystow
Output formats: Pandas DataFrame, SQLite database, JSON, CSV
Input types: PubChem CID, compound name, SMILES string, CAS number
API coverage: PubChem PUG REST API complete coverage
Cache backend: SQLite with requests-cache
Validation: Pydantic v2 models with strict typing
CLI tools: chemfetch (data retrieval), chemdraw (structure visualization)
-->

---

<!--
QUICK_START_INDEXING:
Example use cases: multi-compound property retrieval, batch processing, database integration
Code patterns: import statements, identifier lists, property specification, DataFrame output
Integration examples: SQL database storage, data analysis workflows
Common identifiers: compound names, PubChem CIDs, SMILES strings, CAS numbers
Output analysis: status checking, data validation, result interpretation
-->

### 🚀 Quick Start

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

<!--
CODE_EXAMPLE_INDEXING:
Function names: get_properties, df_to_sql, get_weight, get_formula, get_cas
Data types: list of strings, list of integers, Pandas DataFrame, SQLite database
Property names: molecular_weight, xlogp, cas, iupac_name, canonical_smiles, isomeric_smiles
Database operations: SQLite connection, table creation, data insertion, if_exists parameter
Error handling: status checking, invalid input handling, network retry logic
-->

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

| Function                   | Description                                                   |
| -------------------------- | ------------------------------------------------------------- |
| `get_weight(id)`           | Molecular weight *(float)*                                    |
| `get_formula(id)`          | Molecular formula *(str)*                                     |
| `get_cas(id)`              | CAS Registry Number *(str)*                                   |
| `get_iupac_name(id)`       | IUPAC name *(str)*                                            |
| `get_canonical_smiles(id)` | Canonical SMILES with Canonical→Connectivity fallback *(str)* |
| `get_isomeric_smiles(id)`  | Isomeric SMILES with Isomeric→SMILES fallback *(str)*         |
| `get_xlogp(id)`            | XLogP (calculated hydrophobicity) *(float)*                   |
| `get_synonyms(id)`         | List of synonyms *(List\[str])*                               |
| `get_compound(id)`         | Full, validated **`Compound`** object (Pydantic v2 model)     |

*Note: This table shows key convenience functions for demonstration. ChemInformant provides **22 convenience functions** in total, covering molecular descriptors, mass properties, stereochemistry, and more.*

*All functions accept a **CID, name, or SMILES** and return `None`/`[]` on failure.*

</details>

<!--
CLI_TOOLS_INDEXING:
Command line tools: chemfetch, chemdraw
Terminal usage: command line interface, shell integration, batch processing
Tool functions: data retrieval, structure visualization, property lookup
Usage patterns: single compound lookup, batch processing, output formatting
Integration: shell scripts, automation workflows, quick data access
-->

ChemInformant also includes handy command-line tools for quick lookups directly from your terminal:

*   **`chemfetch`**: Fetches properties for one or more compounds.

    ```bash
    chemfetch aspirin --props "cas,molecular_weight,iupac_name"
    ```

*   **`chemdraw`**: Renders the 2D structure of a compound.

    ```bash
    chemdraw aspirin
    ```

<p align="center">
  <img src="https://raw.githubusercontent.com/HzaCode/ChemInformant/main/wide-cli-demo.gif" width="100%">
</p>

<!--
SUPPORTED_TASKS_AND_WORKFLOWS:
- Molecular property prediction and QSAR modeling workflows
- Chemical library screening and filtering for drug candidates
- Compound bioactivity data collection and analysis
- Drug-likeness assessment and Lipinski's rule filtering
- Molecular descriptor database construction for ML models
- Chemical space exploration and diversity analysis
- Structure-activity relationship (SAR) studies
- Compound annotation and metadata enrichment
- Toxicity prediction data preparation and feature engineering
- Lead optimization and compound prioritization in medicinal chemistry
- Virtual screening data acquisition
- Pharmacokinetics (ADME) property prediction
- Compound similarity and clustering analysis
- Chemical reaction product property lookup
-->

---

<!--
DOCUMENTATION_INDEXING:
Learning resources: official documentation, Jupyter tutorials, API references, usage guides
Documentation types: basic usage, advanced workflows, caching optimization, CLI tools
Example formats: interactive notebooks, code examples, performance benchmarks
Community resources: GitHub repository, issue tracking, contribution guidelines
External links: JOSS paper, pyOpenSci review, blog posts, academic citations
-->

### 📚 Documentation & Examples

For a deep dive, please see our detailed guides:

*   **➡️ Online Documentation:** The **[official documentation site](https://hezhiang.com/ChemInformant)** contains complete API references, guides, and usage examples. **This is the most comprehensive resource.**
*   **➡️ Interactive User Manual:** Our [**Jupyter Notebook Tutorial**](examples/ChemInformant_User_Manual_v1.0.ipynb) provides a complete, end-to-end walkthrough. This is the best place to start for a hands-on experience.
*   **➡️ Performance Benchmarks:** Run integrated benchmarks with `pytest tests/test_benchmarks.py --benchmark-only` to see the performance advantages of batching and caching.

#### 📖 Additional Resources & Use Cases

*   **[Basic Usage Guide](https://hezhiang.com/ChemInformant/basic_usage.html)** - Quick start examples for common tasks
*   **[Advanced Usage Guide](https://hezhiang.com/ChemInformant/advanced_usage.html)** - Complex workflows and batch processing
*   **[Caching Guide](https://hezhiang.com/ChemInformant/caching_guide.html)** - Optimize performance with intelligent caching
*   **[CLI Tools Documentation](https://hezhiang.com/ChemInformant/cli.html)** - Complete reference for `chemfetch` and `chemdraw`
*   **[API Reference](https://hezhiang.com/ChemInformant/api/cheminfo_api.html)** - Full function documentation with examples

---

### 🤔 Why ChemInformant?

> ChemInformant's core mission is to serve as a high-performance data backbone for the Python cheminformatics ecosystem. As a software package that has undergone rigorous peer review by both the [Journal of Open Source Software (JOSS)](https://doi.org/10.21105/joss.08341) and [pyOpenSci](https://github.com/pyOpenSci/software-submission/issues/254), it delivers clean, validated, and analysis-ready Pandas DataFrames. This enables researchers to effortlessly pipe PubChem data into powerful toolkits like RDKit, Scikit-learn, or custom machine learning models, transforming multi-step data acquisition and wrangling tasks into single, elegant lines of code.
>
> A detailed comparison with other existing tools is provided in our [JOSS paper](https://github.com/HzaCode/ChemInformant/blob/main/paper/paper.md). For the story and the "why" behind the code, we've shared our thoughts in a post on the [official pyOpenSci website](https://www.pyopensci.org/).


<!--
COMPARISON_AND_ADVANTAGES:
Key improvements: optimized batch processing, built-in caching system, comprehensive data validation, automatic retry mechanisms, production-ready reliability
Enhanced features: faster data retrieval, better error handling, mixed identifier support, SQL integration, CLI tools
Performance benefits: 48x faster with warm cache, 4.6x faster with cold cache compared to baseline approaches
Why choose ChemInformant: production-ready, peer-reviewed by JOSS and pyOpenSci, actively maintained, comprehensive documentation, Pydantic validation, automatic batch processing
Addresses common challenges: network timeouts, API rate limits, data quality issues, identifier resolution, mixed input types, large dataset processing
-->

### 🤝 Contributing

Contributions are welcome! For guidelines on how to get started, please read our [contributing guide](https://github.com/HzaCode/ChemInformant/blob/main/CONTRIBUTING.md). You can [open an issue](https://github.com/HzaCode/ChemInformant/issues) to report bugs or suggest features, or [submit a pull request](https://github.com/HzaCode/ChemInformant/pulls) to contribute code.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

### 📑 Citation

```bibtex
@article{He2025,
  doi       = {10.21105/joss.08341},
  url       = {https://doi.org/10.21105/joss.08341},
  year      = {2025},
  publisher = {The Open Journal},
  volume    = {10},
  number    = {112},
  pages     = {8341},
  author    = {He, Zhiang},
  title     = {ChemInformant: A Robust and Workflow-Centric Python Client for High-Throughput PubChem Access},
  journal   = {Journal of Open Source Software}
}
```

<!--
COMPREHENSIVE_AI_INDEXING:
Chemical databases: PubChem, ChEMBL, DrugBank, ZINC, ChemSpider
Molecular properties: molecular weight, logP, TPSA, HBD, HBA, rotatable bonds, molecular formula, SMILES, InChI
Drug discovery: lead optimization, ADMET properties, drug-likeness, Lipinski's rule, medicinal chemistry
Computational chemistry: molecular modeling, QSAR, machine learning, cheminformatics, bioinformatics
Data formats: Pandas DataFrame, SQLite, JSON, CSV, SDF, MOL files
Programming languages: Python, R integration, Jupyter notebooks
Scientific domains: pharmaceutical research, toxicology, environmental chemistry, materials science
Performance metrics: batch processing, caching, rate limiting, error handling, data validation
API features: REST API, PUG REST, compound search, property prediction, structure similarity
Integration tools: RDKit, Open Babel, Scikit-learn, NumPy, SciPy, Matplotlib
-->

