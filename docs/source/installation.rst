============
Installation
============

This guide will walk you through the installation of ChemInformant. We recommend using Python 3.8 or higher.

--------------------------------------
Installation via PyPI (Recommended)
--------------------------------------

The most stable and convenient way to install ChemInformant is via `pip` from the Python Package Index (PyPI). This is suitable for the vast majority of users.

.. code-block:: bash

   pip install ChemInformant

This command will install the core version of the library, which includes all data fetching and processing functionalities.

Installation with Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some features of ChemInformant (such as plotting) depend on extra libraries. You can install them together by specifying "extras".

*   **To install plotting functionality:**
    If you want to use data visualization features, such as the :func:`~ChemInformant.draw_compound` function or the ``chemdraw`` command-line tool, please install the version with the ``[plot]`` extra:

    .. code-block:: bash

       pip install "ChemInformant[plot]"

    This will additionally install `matplotlib`, `Pillow`, `seaborn`, and `scikit-learn`.

---------------------------------------------
Installation from Source (For Developers)
---------------------------------------------

If you wish to get the latest, unreleased development version, or if you plan to contribute code to the project, you can install it from the source code.

1.  First, clone the project repository from GitHub to your local machine:

    .. code-block:: bash

       git clone https://github.com/HzaCode/ChemInformant.git

2.  Next, navigate into the project's root directory:

    .. code-block:: bash

       cd ChemInformant

3.  Finally, use `pip` for a local installation. We strongly recommend using **editable mode** (`-e`), so that any changes you make to the source code will take effect immediately without needing to reinstall.

    *   **To set up a complete environment for development contribution:**
        This command will install all dependencies, including the core library, plotting functionality, and development tools for testing and code checking (like `pytest`, `black`). This is the recommended command for contributors.

        .. code-tally-block:: bash

           pip install -e .[all]

    *   **To install only the core package from source:**
        If you just want to install a basic version from the source code for general use.

        .. code-block:: bash

           pip install .