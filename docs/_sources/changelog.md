# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Your new features here)

### Changed
- (Changes in existing functionality)

## [1.2.0] - YYYY-MM-DD

### Added
- **New `fig` function**: Added functionality to retrieve and display 2D chemical structure images directly from PubChem (e.g., in Jupyter Notebooks or interactive Python environments).
- Expanded core functionality for fetching various compound data points from PubChem by name or CID, supporting the new image display feature.
- Implemented a robust caching mechanism using `requests-cache` to improve performance and reduce API calls.
- Ensured data integrity and type safety through Pydantic model validation.
- Provided utility functions for batch retrieval of compound information.

### Changed
- Significantly improved test coverage to over 90%, including tests for the new `fig` functionality.
- Standardized code style across the project using Black and addressed all Flake8 linting issues.

### Deprecated
- (Soon-to-be removed features)

### Removed
- (Removed features)

### Fixed
- (Any bug fixes)

### Security
- (In case of vulnerabilities)

## [1.2.0] - YYYY-MM-DD

### Added
- Initial public release.
- Core functionality for fetching compound data from PubChem by name or CID.
- Caching mechanism using `requests-cache`.
- Data validation using Pydantic models.
- Functions for batch retrieval of compound information.
- Function to display 2D chemical structures (`fig`).

### Changed
- Improved test coverage to over 90%.
- Applied Black and Flake8 for code style consistency. 