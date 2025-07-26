==================================
Data Models and Exceptions (`models`)
==================================

.. module:: ChemInformant.models

This module is the core of the library's data contract, responsible for enforcing data integrity and providing clear error signals. It leverages Pydantic to transform unstructured API responses into robust, type-safe Python objects.

By defining clear data models, this module ensures that all data consumed by the application layer is valid and predictable.

.. rubric:: Data Models

.. autoclass:: ChemInformant.models.Compound
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource
   :exclude-members: __init__
   :no-value:

.. rubric:: Custom Exceptions

.. autoexception:: ChemInformant.models.NotFoundError
   :show-inheritance:

.. autoexception:: ChemInformant.models.AmbiguousIdentifierError
   :show-inheritance: