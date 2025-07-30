===========================
ChemInformant Documentation
===========================

Welcome to the official documentation for **ChemInformant** - a robust data acquisition engine for the PubChem database, engineered for the modern scientific workflow.

**Key Features:**

* 📊 **Analysis-Ready Pandas/SQL Output** - Clean DataFrames and direct SQL export, eliminating data wrangling boilerplate  
* 🔄 **Automated Network Reliability** - Built-in persistent caching, smart rate-limiting, and automatic retries  
* 🎯 **Flexible & Fault-Tolerant Input** - Mixed identifiers (names, CIDs, SMILES) with intelligent error handling  
* ⚡ **Efficient Batch Processing** - Retrieve multiple compounds and properties in single API calls with automatic pagination  
* 🔧 **22 Convenience Functions** - Quick access to individual properties like ``get_weight()``, ``get_formula()``, ``get_cas()``  
* ⚡ **Dual API for Simplicity and Power** - Convenience layer backed by powerful ``get_properties`` batch engine  
* 🛡️ **Guaranteed Data Integrity** - Pydantic v2 models for rigorous runtime data validation  
* 💻 **Terminal-Ready CLI Tools** - ``chemfetch`` and ``chemdraw`` for rapid data retrieval and visualization  
* 🆕 **Modern and Actively Maintained** - Contemporary tech stack for long-term reliability

This page serves as the central entry point for all feature modules, guides, and API references.

.. toctree::
   :caption: 🧭 User Guide
   :maxdepth: 2

   installation
   basic_usage
   advanced_usage
   cli
   caching_guide

.. toctree::
   :caption: 🎓 Tutorials
   :maxdepth: 1

   tutorials

.. toctree::
   :caption: 🔬 API Reference
   :maxdepth: 2

   api/cheminfo_api
   api/models
   api/api_helpers

.. toctree::
   :caption: 🛠️ Project Information
   :maxdepth: 1

   contributing
