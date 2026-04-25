# Delta for Index Generation

## MODIFIED Requirements

### Requirement: Build a structured star index
The system SHALL normalize fetched star data into a stable local representation and generate a browsable XML index, a raw JSON cache, a Markdown summary, and a machine-readable manifest without requiring source edits for a new user or output location.

#### Scenario: Build uses explicit CLI inputs instead of source edits
- GIVEN a user installs the packaged CLI
- WHEN the user runs the build command with a GitHub username and output location
- THEN the system SHALL generate the primary artifacts without requiring edits to repository source files

#### Scenario: Build publishes a manifest
- GIVEN a successful build
- WHEN artifact generation completes
- THEN the system SHALL write a manifest describing generated artifacts, counts, schema version, and source user

### Requirement: Categorize repositories for LLM use
The system SHALL assign each indexed repository one or more LLM-oriented categories using deterministic rules and optional manual overrides, and it SHALL preserve provenance showing whether each category came from inference or manual mapping.

#### Scenario: Category provenance is preserved
- GIVEN a repository has both inferred and manual categories
- WHEN the repository is written to output artifacts
- THEN the system SHALL identify the provenance of each category entry
- AND downstream bundle artifacts SHALL be able to consume that provenance
