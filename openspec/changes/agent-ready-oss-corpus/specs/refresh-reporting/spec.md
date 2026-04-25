# Delta for Refresh Reporting

## MODIFIED Requirements

### Requirement: Report additions and removals between refreshes
The system SHALL write both a human-readable change report and a machine-readable change artifact showing how the starred repository set changed between the previous cache and the current refresh.

#### Scenario: Refresh publishes machine-readable diff data
- GIVEN the refresh workflow completes
- WHEN the starred repository set has been compared to the previous cache
- THEN the system SHALL publish a machine-readable diff artifact or manifest entry for added and removed repositories
- AND the human-readable Markdown report SHALL remain available
