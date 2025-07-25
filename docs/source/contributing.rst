=======================
Contributing Guide
=======================

First of all, thank you for considering contributing to ChemInformant! We welcome and value the participation of every contributor. Whether it's reporting bugs, suggesting feature enhancements, seeking support, or writing code, your help is crucial.

This document provides guidelines for contributing, aiming to make the entire process as smooth as possible for everyone involved.

.. contents:: Contents
   :local:
   :depth: 2

--------------------
How to Contribute
--------------------

*   **Getting Help:** If you have questions about how to use the project, feel free to `create an issue <https://github.com/HzaCode/ChemInformant/issues>`__.
*   **Reporting Bugs:** If you find a bug, please report it via `GitHub Issues <https://github.com/HzaCode/ChemInformant/issues>`__.
*   **Suggesting Enhancements:** Have ideas for new features or improvements? Please `create an issue <https://github.com/HzaCode/ChemInformant/issues>`__ to discuss them.
*   **Submitting Pull Requests:** Contribute code to fix bugs or add new features.

---------------------------------
Seeking Support or Asking Questions
---------------------------------

If you have questions about how to use ChemInformant, or if you're not sure whether you've encountered a bug, the best place to ask is the `GitHub Issues page <https://github.com/HzaCode/ChemInformant/issues>`__.

When creating an issue for support, please ensure that you:

#. **First, search existing issues** to see if your question has already been answered.
#. Provide a clear and descriptive title.
#. Explain what you are trying to achieve and the problem you are facing.
#. If possible, include a small, self-contained code snippet to illustrate your problem.

--------------------
Reporting Bugs
--------------------

Before submitting a bug report, please check the existing `GitHub Issues <https://github.com/HzaCode/ChemInformant/issues>`__ to confirm that the bug has not already been reported.

If it has not been reported, please create a new issue and include the following information:

*   **ChemInformant Version:** (e.g., obtained via ``ChemInformant.__version__``)
*   **Python Version:**
*   **Operating System:**
*   **Description of the Bug:** A clear description of the problem.
*   **Steps to Reproduce:** Provide a minimal, complete, and verifiable code example to trigger the bug.
*   **Expected Behavior:** What you expected to happen.
*   **Actual Behavior:** What actually happened (including any error messages or stack traces).

---------------------------
Suggesting Enhancements
---------------------------

We are open to suggestions for new features or improvements. Before submitting an enhancement suggestion:

*   Please check the existing `GitHub Issues <https://github.com/HzaCode/ChemInformant/issues>`__ to see if a similar idea has already been discussed.
*   Create a new issue.
*   Clearly describe your proposed enhancement and its **motivation** (what problem does it solve?).
*   If possible, provide examples of how the feature might be used.

---------------------------
Code Contribution Process
---------------------------

Ready to contribute code? Here’s how to set up ``ChemInformant`` for local development and submit your changes.

Development Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  **Fork the repository:** Click the "Fork" button on the `ChemInformant GitHub page <https://github.com/HzaCode/ChemInformant>`__.

2.  **Clone your fork:**

    .. code-block:: bash

       git clone https://github.com/YOUR_USERNAME/ChemInformant.git
       cd ChemInformant

3.  **Create a virtual environment:** It is highly recommended to use a virtual environment (e.g., ``venv``, ``conda``).

    .. code-block:: bash

       # Using venv
       python -m venv .venv
       source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

4.  **Install dependencies:** Install the package in editable mode along with its development dependencies (like ``pytest``, ``black``).

    .. code-block:: bash

       pip install -e .[dev]

5.  **Create a branch:** Create a new branch for your changes.

    .. code-block:: bash

       git checkout -b your-feature-or-bugfix-branch

Code Style
~~~~~~~~~~~~

*   ChemInformant follows the **PEP 8** style guide.
*   We use **Black** for automatic code formatting. Before committing your changes, please run Black to format your code:

    .. code-block:: bash

       black .

Running Tests
~~~~~~~~~~~~~~~

*   We use ``pytest`` for testing. Please ensure all tests pass before submitting a pull request.
*   Add new test cases for any new features or bug fixes you introduce. We aim to maintain high test coverage.
*   Run the tests from the root directory of the repository:

    .. code-block:: bash

       pytest tests/

Submitting a Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1.  Make your code changes, write tests, and format your code with Black.
2.  Commit your changes with a clear and descriptive commit message.
3.  Push your branch to your fork on GitHub:

    .. code-block:: bash

       git push origin your-feature-or-bugfix-branch

4.  Create a Pull Request on the ChemInformant GitHub repository.
5.  Set the target branch to the ``main`` branch of the original repository.
6.  Provide a clear title and description for your PR. Explain the "why" and "what" of your changes.
7.  Link to any relevant GitHub Issues (e.g., "Closes #123").
8.  Wait for the automated checks (like CI tests) to pass.
9.  Be prepared to respond to any feedback or review comments.

-----------------
Code of Conduct
-----------------

Please note that this project is governed by the Contributor Code of Conduct. By participating in this project, you agree to abide by its terms. All participants are expected to uphold the Code of Conduct in all project spaces, including Issues, Pull Requests, and other communication channels. For details, please see the ``CODE_OF_CONDUCT.md`` file in the project's root directory.

Thank you again for your contribution!```