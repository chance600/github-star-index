# Index Generation

## Requirement: Fetch starred repositories from GitHub
The system SHALL fetch a GitHub user's starred repositories from the GitHub REST starring API and preserve the star timestamp when the API exposes it.

#### Scenario: Authenticated fetch uses available credentials
- GIVEN the operator runs the generator on a machine with `GH_TOKEN`, `GITHUB_TOKEN`, or a valid local `gh` login
- WHEN the generator builds the index
- THEN it SHALL use one of those credentials for GitHub API requests
- AND it SHALL avoid printing the credential value

#### Scenario: Public fetch works without credentials
- GIVEN the operator runs the generator without any credential
- WHEN the starred repositories are publicly accessible
- THEN the generator SHALL attempt anonymous GitHub API requests
- AND it SHALL return a clear rate-limit or network error when the anonymous path is insufficient

## Requirement: Build a structured star index
The system SHALL normalize fetched star data into a stable local representation and generate a browsable XML index, a raw JSON cache, and a Markdown summary.

#### Scenario: Build writes all primary artifacts
- GIVEN a successful star fetch
- WHEN the build completes
- THEN the system SHALL write a raw JSON cache containing the fetched star payload
- AND it SHALL write an XML index with repository metadata and summaries
- AND it SHALL write a Markdown summary with counts and highlights

#### Scenario: Offline rebuild uses cached raw data
- GIVEN a previously written raw JSON cache
- WHEN the operator runs the build in offline mode
- THEN the system SHALL rebuild the XML index and Markdown summary without calling the GitHub API

## Requirement: Categorize repositories for LLM use
The system SHALL assign each indexed repository one or more LLM-oriented categories using deterministic rules and optional manual overrides.

#### Scenario: Inferred categories use repository metadata
- GIVEN repository language, description, and topics are available
- WHEN the generator categorizes the repository
- THEN it SHALL infer one or more categories from deterministic local rules
- AND it SHALL preserve category ordering in the generated XML

#### Scenario: Manual category overrides win where provided
- GIVEN `config/manual_categories.json` contains overrides for a repository or topic
- WHEN the repository is categorized
- THEN the generated output SHALL include those manual categories alongside inferred categories
- AND manual `llm_use` hints SHALL take precedence for that repository
