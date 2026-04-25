# Delta for Artifact Bundles

## ADDED Requirements

### Requirement: Generate agent-ready repository bundle records
The system SHALL generate per-repository bundle records optimized for LLM and agent ingestion from the normalized star dataset.

#### Scenario: Repository bundle records are emitted
- GIVEN normalized star data exists locally
- WHEN the operator runs the bundle workflow
- THEN the system SHALL write one or more machine-readable bundle files
- AND each repository record SHALL include stable identity fields, core metadata, category labels, and `llm_use` guidance

### Requirement: Generate chunked corpus artifacts
The system SHALL generate chunked corpus artifacts suitable for long-context prompts or retrieval pipelines.

#### Scenario: Chunk records include ordering and provenance
- GIVEN a repository record or enrichment payload is larger than a single chunk target
- WHEN the bundle workflow emits chunked output
- THEN each chunk SHALL include a stable chunk identifier
- AND it SHALL include repository reference, chunk order, chunk count, and provenance fields

### Requirement: Preserve artifact provenance
The system SHALL annotate bundle outputs with provenance so downstream users can identify which fields came from GitHub metadata, manual taxonomy, inferred taxonomy, or optional enrichment.

#### Scenario: Provenance distinguishes metadata from enrichment
- GIVEN README enrichment is enabled for a build
- WHEN bundle artifacts are written
- THEN records derived from README content SHALL be marked as README-derived
- AND records derived only from repository metadata SHALL remain distinguishable

### Requirement: Bundle generation remains local-first
The system SHALL allow bundle generation from cached normalized data without requiring a fresh network fetch.

#### Scenario: Offline bundle build succeeds from cache
- GIVEN the normalized cache and optional snapshots already exist locally
- WHEN the operator runs bundle generation without network access
- THEN the system SHALL generate bundle outputs from cached inputs only
