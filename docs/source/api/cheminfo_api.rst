=============================
Main API Interface (`cheminfo_api`)
=============================

.. module:: ChemInformant.cheminfo_api

This module is the main entry point for all user interactions. It is designed around two core philosophies to cater to different use cases:

1.  **Bulk Data Retrieval (Engine):** The :py:func:`get_properties` function is the workhorse of this library. It achieves maximum efficiency by fetching multiple properties for multiple compounds in a single, consolidated API call. It returns a Pandas DataFrame, making it ideal for data analysis, scripting, and integration with the scientific computing ecosystem (e.g., RDKit, Scikit-learn).

2.  **Convenience and Object-Oriented Access (Interface):** A series of ``get_<property>()`` functions provide direct access to individual data points. For scenarios requiring comprehensive, type-safe data, :py:func:`get_compound` returns a fully validated Pydantic :py:class:`~ChemInformant.models.Compound` object.

.. rubric:: Core Bulk Processing Function

.. autofunction:: get_properties

.. rubric:: Object-Oriented Fetchers

.. autofunction:: get_compound
.. autofunction:: get_compounds

.. rubric:: Convenience Lookups

.. autofunction:: get_weight
.. autofunction:: get_formula
.. autofunction:: get_cas
.. autofunction:: get_iupac_name
.. autofunction:: get_canonical_smiles
.. autofunction:: get_isomeric_smiles
.. autofunction:: get_xlogp
.. autofunction:: get_synonyms

.. rubric:: Visualization Functions

.. autofunction:: draw_compound