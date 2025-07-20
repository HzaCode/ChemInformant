
# Contributing to ChemInformant

First off, thank you for considering contributing to ChemInformant! We welcome and value contributions from everyone. Whether it's reporting a bug, suggesting an enhancement, seeking support, or writing code, your help is appreciated.

This document provides guidelines for contributing to make the process as smooth as possible for everyone involved.

## Table Of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Seeking Support or Asking Questions](#seeking-support-or-asking-questions)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Your First Code Contribution](#your-first-code-contribution)
  - [Setting Up Your Development Environment](#setting-up-your-development-environment)
  - [Code Style](#code-style)
  - [Running Tests](#running-tests)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Code of Conduct](#code-of-conduct)

## Ways to Contribute

- **Ask for Help:** If you have questions about how to use the project, please open an issue.
- **Report Bugs:** If you find a bug, please report it using [GitHub Issues](https://github.com/HzaCode/ChemInformant/issues).
- **Suggest Enhancements:** Have an idea for a new feature or an improvement? Open an issue to discuss it.
- **Submit Pull Requests:** Contribute code to fix bugs or add new features.

## Seeking Support or Asking Questions

If you have a question about how to use ChemInformant or are not sure if you've encountered a bug, the best place to ask is the [GitHub Issues page](https://github.com/HzaCode/ChemInformant/issues).

When you open an issue for support, please be sure to:
1.  **Search existing issues** first to see if your question has already been answered.
2.  Provide a clear and descriptive title.
3.  Explain what you are trying to achieve and what problem you are facing.
4.  If possible, include a small, self-contained code snippet to illustrate your question.

## Reporting Bugs

Before submitting a bug report, please check the existing [GitHub Issues](https://github.com/HzaCode/ChemInformant/issues) to see if the bug has already been reported.

If it hasn't, please open a new issue and include the following information:

- **ChemInformant Version:** (e.g., from `ChemInformant.__version__`)
- **Python Version:**
- **Operating System:**
- **Description of the Bug:** Clearly describe the issue.
- **Steps to Reproduce:** Provide a minimal, complete, and verifiable code example that triggers the bug.
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
    git clone https://github.com/YOUR_USERNAME/ChemInformant.git
    cd ChemInformant
    ```
3.  **Create a Virtual Environment:** It's highly recommended to use a virtual environment (e.g., `venv`, `conda`).
    ```bash
    # Using venv
    python -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```
4.  **Install Dependencies:** Install the package in editable mode along with development dependencies (like `pytest`, `black`). Assuming a `dev` extra is defined in your `pyproject.toml`:
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
- We use **Black** for automatic code formatting. Before committing your changes, please run Black to format your code:
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

### Submitting Pull Requests

1.  Make your changes, write tests, and format your code with Black.
2.  Commit your changes with a clear and descriptive commit message.
3.  Push your branch to your fork on GitHub:
    ```bash
    git push origin your-feature-or-bugfix-branch
    ```
4.  Open a Pull Request (PR) on the ChemInformant GitHub repository.
5.  Target the `main` branch of the original repository.
6.  Provide a clear title and description for your PR. Explain the "why" and "what" of your changes.
7.  Link to any relevant GitHub issues (e.g., "Closes #123").
8.  Wait for the automated checks (like CI tests) to pass.
9.  Be prepared to respond to any feedback or review comments.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project, you agree to abide by its terms. All participants are expected to follow the Code of Conduct in all project spaces, including issues, pull requests, and any other communication channels. Please see the `CODE_OF_CONDUCT.md` file for details.

Thank you again for your contribution!
