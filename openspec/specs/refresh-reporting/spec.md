# Refresh Reporting

## Requirement: Refresh the index from current GitHub state
The system SHALL provide a refresh workflow that rebuilds the current star index from GitHub and compares the result to the previous cached state.

#### Scenario: Refresh rebuilds the primary artifacts
- GIVEN a prior raw JSON cache may or may not exist
- WHEN the operator runs the refresh workflow
- THEN the system SHALL invoke the index build
- AND it SHALL leave the XML index, raw JSON cache, and Markdown summary in sync with the newest successful fetch

## Requirement: Report additions and removals between refreshes
The system SHALL write a human-readable change report showing how the starred repository set changed between the previous cache and the current refresh.

#### Scenario: Refresh detects no changes
- GIVEN the current starred repository set matches the previous cached set
- WHEN refresh completes
- THEN the change report SHALL record the before and after counts
- AND it SHALL state that no repositories were added or removed

#### Scenario: Refresh detects added and removed repositories
- GIVEN the current starred repository set differs from the previous cached set
- WHEN refresh completes
- THEN the change report SHALL list added repositories
- AND it SHALL list removed repositories
- AND each listed repository SHALL include a stable identifier and GitHub URL
