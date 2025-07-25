================================
Internal API Helpers (`api_helpers`)
================================

.. module:: ChemInformant.api_helpers

This module serves as the low-level networking foundation for the ChemInformant library. It is responsible for handling direct communication with the PubChem API, encapsulating complexities such as HTTP session management, persistent caching, request rate limiting, and robust retry logic against network or server failures.

Functions within this module are considered internal implementation details and **are not recommended for direct invocation by end-users**. Users should interact with this library through the high-level functions defined in :py:mod:`~ChemInformant.cheminfo_api`.

.. note::
   Private functions within this module (those starting with an underscore, like ``_fetch_with_ratelimit_and_retry``) are not documented here as they represent internal implementation details.

---

.. rubric:: Session and Cache Management

Functions for setting up and managing the cached HTTP session.

.. autofunction:: setup_cache

.. autofunction:: get_session

---

.. rubric:: Data Fetching Functions

These functions wrap specific PubChem API endpoints to retrieve data.

.. autofunction:: get_cids_by_name

.. autofunction:: get_cids_by_smiles

.. autofunction:: get_batch_properties

.. autofunction:: get_cas_for_cid

.. autofunction:: get_synonyms_for_cid