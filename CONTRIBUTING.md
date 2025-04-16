# Contributing to ChemInformant

First off, thank you for considering contributing to ChemInformant! We welcome contributions from everyone. Whether it's reporting a bug, suggesting an enhancement, improving documentation, or writing code, your help is valuable.

This document provides guidelines for contributing to make the process smooth for everyone involved.

## Table Of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Your First Code Contribution](#your-first-code-contribution)
  - [Setting Up Your Development Environment](#setting-up-your-development-environment)
  - [Code Style](#code-style)
  - [Running Tests](#running-tests)
  - [Writing Documentation](#writing-documentation)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Code of Conduct](#code-of-conduct)

## Ways to Contribute

- **Report Bugs:** If you find a bug, please report it using [GitHub Issues](https://github.com/HzaCode/ChemInformant/issues).
- **Suggest Enhancements:** Have an idea for a new feature or an improvement? Open an issue to discuss it.
- **Write Documentation:** Good documentation is crucial. Help us improve the docs, tutorials, or examples.
- **Submit Pull Requests:** Contribute code to fix bugs or add new features.

## Reporting Bugs

Before submitting a bug report, please check the existing [GitHub Issues](https://github.com/HzaCode/ChemInformant/issues) to see if the bug has already been reported.

If it hasn't, please open a new issue and include the following information:

- **ChemInformant Version:** (e.g., from `ChemInformant.__version__`)
- **Python Version:**
- **Operating System:**
- **Description of the Bug:** Clearly describe the issue.
- **Steps to Reproduce:** Provide a minimal code example that triggers the bug.
- **Expected Behavior:** What you expected to happen.
- **Actual Behavior:** What actually happened (including any error messages or tracebacks).

## Suggesting Enhancements

We are open to suggestions for new features or improvements. Before submitting an enhancement suggestion:

- Check the existing [GitHub Issues](https://github.com/HzaCode/ChemInformant/issues) to see if a similar idea has already been discussed.
- Open a new issue.
- Clearly describe the proposed enhancement and the **motivation** behind it (what problem does it solve?).
- If possible, provide examples of how the feature might be used.

## Your First Code Contribution

Ready to contribute code? Here’s how to set up `ChemInformant` for local development and submit your changes.

### Setting Up Your Development Environment

1.  **Fork the Repository:** Click the "Fork" button on the [ChemInformant GitHub page](https://github.com/HzaCode/ChemInformant).
2.  **Clone Your Fork:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/ChemInformant.git](https://github.com/YOUR_USERNAME/ChemInformant.git)
    cd ChemInformant
    ```
3.  **Create a Virtual Environment:** It's highly recommended to use a virtual environment (e.g., `venv`, `conda`).
    ```bash
    # Using venv
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```
4.  **Install Dependencies:** Install the package in editable mode along with development dependencies (like `pytest`, `black`). You might need to define these in your `pyproject.toml` under `[project.optional-dependencies]`. Assuming a `dev` extra:
    ```bash
    pip install -e .[dev]
    # If you don't have a [dev] extra defined yet, install manually:
    # pip install -e .
    # pip install pytest requests-cache black
    ```
5.  **Create a Branch:** Create a new branch for your changes.
    ```bash
    git checkout -b your-feature-or-bugfix-branch
    ```

### Code Style

- ChemInformant follows the **PEP 8** style guide.
- We use **Black** for automatic code formatting. Before committing your changes, please run Black:
  ```bash
  black .
  ```

### Running Tests

- We use `pytest` for testing. Please ensure all tests pass before submitting a pull request.
- Add new tests for any new features or bug fixes you introduce. We aim for high test coverage.
- Run tests from the root directory of the repository:
  ```bash
  pytest tests/
  ```

### Writing Documentation

- If your changes affect user-facing behavior or add new features, please update the documentation in the `docs/source` directory.
- We use Sphinx to build the documentation. Make sure your docstrings are clear and follow the Google style format.
- Build the documentation locally to check for errors and rendering:
  ```bash
  # Navigate to the docs/ directory
  cd docs
  make html
  # Open docs/build/html/index.html in your browser
  ```

### Submitting Pull Requests

1.  Make your changes, write tests, update documentation, and format your code with Black.
2.  Commit your changes with a clear commit message.
3.  Push your branch to your fork on GitHub:
    ```bash
    git push origin your-feature-or-bugfix-branch
    ```
4.  Open a Pull Request (PR) on the ChemInformant GitHub repository.
5.  Target the `main` branch of the original repository.
6.  Provide a clear title and description for your PR.
7.  Link to any relevant GitHub issues (e.g., "Closes #123").
8.  Wait for the automated checks (like CI tests) to pass.
9.  Respond to any feedback or review comments.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms. See the `CODE_OF_CONDUCT.md` file for details.

Thank you again for your contribution!
