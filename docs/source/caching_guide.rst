=============
Caching Guide
=============

This guide provides a comprehensive overview of the caching mechanism in ChemInformant. You will learn how to use the ``setup_cache()`` function to enable, configure, and manage the cache, significantly improving script performance and ensuring reproducible results.

.. contents:: Table of Contents
   :depth: 2
   :local:

---

1. Why Caching is Essential
===========================

When interacting with web APIs like PubChem, you may encounter rate limits or temporary server issues (like ``503 Service Unavailable`` errors). A persistent cache solves these problems by storing API responses on your local disk.

*   **Speed**: Subsequent identical requests are served instantly from the cache, reducing execution time from seconds to milliseconds.
*   **Reliability**: It makes your scripts robust against temporary network failures or API downtime.
*   **Reproducibility**: Your analysis scripts can be re-run offline, yielding the exact same data.

---

2. Quick Start
================

Enabling the cache is straightforward. Simply call the ``setup_cache()`` function once at the beginning of your script.

.. code-block:: python
   :caption: Enabling the default cache

   import ChemInformant as ci

   # Call this once to enable the default 7-day cache
   ci.setup_cache()

   # All subsequent API calls will now automatically use the cache
   info = ci.get_compound("Aspirin")

3. Core Configuration: Understanding ``setup_cache()``
======================================================

The ``setup_cache()`` function provides a rich set of parameters, allowing you to fine-tune caching behavior.

.. autofunction:: ChemInformant.api_helpers.setup_cache
   :noindex:

3.1. `expire_after`: Setting Cache Freshness
--------------------------------------------

This parameter controls how long cached responses remain valid. You can provide the value in several convenient formats.

.. code-block:: python
   :caption: Different ways to set expiration

   from datetime import timedelta
   import ChemInformant as ci

   # Method 1: Use a human-readable string ("d" for day, "h" for hour)
   ci.setup_cache(expire_after="1d")

   # Method 2: Use seconds directly (e.g., 1 hour = 3600 seconds)
   ci.setup_cache(expire_after=3600)

   # Special values: -1 means the cache never expires, 0 disables caching
   ci.setup_cache(expire_after=-1)


3.2. `backend`: Choosing a Storage Backend
------------------------------------------

You can choose the most suitable storage backend for your use case.

.. list-table:: Available Cache Backends
   :widths: 20 20 60
   :header-rows: 1

   * - Backend
     - Dependencies
     - Use Case
   * - ``'sqlite'``
     - (none)
     - **Default option.** The most versatile file-based cache, ideal for single-machine environments.
   * - ``'memory'``
     - (none)
     - In-memory cache. The fastest option, but the cache is discarded when the script finishes.
   * - ``'redis'``
     - ``redis``
     - Use when you need to share a cache across multiple processes or machines.

---

4. Managing Your Cache
======================

4.1. Clearing the Cache
-----------------------

*   **Manual Deletion**: The most direct way is to delete the entire cache directory.

    .. code-block:: bash

       # On Linux/macOS
       rm -rf ~/.data/cheminformant/cache/

*   **Programmatic Clearing**: Get the session object via `get_session()` and call its clear method.

    .. code-block:: python

       session = ci.get_session()
       session.cache.clear() # This will delete all cached entries

4.2. Temporarily Disabling the Cache
------------------------------------

If you want to run a script without using the persistent cache, simply switch the backend to ``'memory'``.

.. code-block:: python

   ci.setup_cache(backend="memory") # The cache for this session will be discarded on exit

---

5. Advanced Usage: Fine-Grained Path Control with PyStow
========================================================

For advanced users who need precise control over data storage locations, ChemInformant leverages the powerful **PyStow** library for path management. This allows you to easily redirect the cache directory to other disks or adhere to specific operating system standards.

5.1. Understanding How PyStow Works
-----------------------------------
PyStow's core mission is to provide a unified, predictable, and configurable storage location for Python applications.

*   **Default Behavior**: It creates a ``.data`` directory in your user's home folder and then organizes data in subdirectories named after the application (in this case, `cheminformant`).
    *   **Linux/macOS Default Path**: ``~/.data/cheminformant/cache/``
    *   **Windows Default Path**: ``%USERPROFILE%\.data\cheminformant\cache\``

5.2. Customizing Paths via Environment Variables
------------------------------------------------
This is the most flexible and recommended way to configure PyStow, as it requires no code changes.

.. list-table:: Core PyStow Environment Variables
   :widths: 30 70
   :header-rows: 1

   * - Environment Variable
     - Description & Effect
   * - ``CHEMINFORMANT_HOME``
     - **Recommended Usage.** Sets a new base directory for ChemInformant *only*. This is the most precise and non-interfering way to configure paths.
       **Example**: ``export CHEMINFORMANT_HOME=/mnt/ssd/data``
   * - ``PYSTOW_HOME``
     - **Global Configuration.** Sets a new global base directory for *all* applications that use PyStow. A good choice if you want to centralize all your scientific data.
       **Example**: ``export PYSTOW_HOME=/data/``
   * - ``PYSTOW_USE_APPDIRS``
     - **Follow System Standards.** Setting this variable to ``true`` makes PyStow follow the XDG Base Directory Specification.
       - **Linux/macOS**: The cache will be stored in ``~/.cache/cheminformant/``
       - **Windows**: The cache will be stored in ``%LOCALAPPDATA%\ChemInformant\Cache\``
   * - ``PYSTOW_NAME``
     - **Modify Default Directory Name.** Replaces the default ``.data`` directory name with one you specify.
       **Example**: ``export PYSTOW_NAME=.my_apps_data``

5.3. Configuration Priority
---------------------------
PyStow follows a clear priority order to determine the final path:

1.  The **application-specific variable** (``CHEMINFORMANT_HOME``) has the highest priority.
2.  If not set, the **global variable** (``PYSTOW_HOME``) is used.
3.  If neither is set, the **default path** is used (based on ``~/.data`` or the XDG specification).

.. admonition:: Diving Deeper into PyStow
   :class: tip

   This guide only covers the most common features of PyStow as used in ChemInformant. If you want to explore more advanced use cases, such as dynamic configuration via the Python API, path lookups, and more, we highly recommend reading `PyStow's official GitHub repository <https://github.com/cthoyt/pystow>`_.