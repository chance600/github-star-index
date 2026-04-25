# Delta for Distribution

## ADDED Requirements

### Requirement: Ship as an installable CLI package
The system SHALL be installable as a standard Python package with a documented CLI entrypoint.

#### Scenario: New user installs and runs the CLI
- GIVEN a new user clones the repository or installs the package from a distribution artifact
- WHEN the user runs the documented install and build commands
- THEN the CLI SHALL execute without requiring the user to modify package source files

### Requirement: Publish OSS-safe fixtures and examples
The repository SHALL include sample fixtures and example outputs that do not depend on personal private star data.

#### Scenario: Public examples avoid personal generated data
- GIVEN the repository is prepared for open source publication
- WHEN examples and tests are reviewed
- THEN they SHALL use synthetic or public-safe fixture data
- AND they SHALL not require committing a personal live star index

### Requirement: Validate behavior in CI
The repository SHALL provide automated checks for the package CLI and generated artifacts.

#### Scenario: CI verifies artifact contracts
- GIVEN a pull request modifies bundle or index generation
- WHEN CI runs
- THEN it SHALL execute tests for normalization and artifact generation
- AND it SHALL verify that generated artifact counts and schemas remain consistent
