# Design: agent-ready OSS corpus builder

## Overview
The current repository has a useful core: fetch stars, infer categories, write XML/JSON/Markdown, and report diffs. The design goal is to preserve that deterministic core while making the project installable, configurable, and clearly optimized for agent-ready artifact generation.

This change does not add a hosted system. It packages a local engine.

## Design Goals
- Preserve deterministic behavior for existing primary artifacts.
- Remove hardcoded personal assumptions from the CLI and repository layout.
- Add corpus-oriented outputs that are more useful to LLM and agent workflows than a single monolithic XML file.
- Keep dependencies modest and optional features isolated.
- Make the repository publishable as an OSS package.

## Non-Goals
- No vector store dependency.
- No mandatory LLM calls.
- No web UI.
- No GitHub write operations in v1.

## User Workflows

### Workflow 1: Basic export
1. User installs the package.
2. User runs `star-index build --user <github-user>`.
3. Tool fetches stars and writes raw JSON, XML, summary, and manifest.

### Workflow 2: Automation refresh
1. User schedules `star-index refresh`.
2. Tool fetches the latest stars.
3. Tool updates primary artifacts and emits diff reports.
4. Automation inbox or CI consumes the report.

### Workflow 3: Agent-ready corpus generation
1. User runs `star-index bundle`.
2. Tool reads the normalized cache and optional README snapshots.
3. Tool emits JSONL bundle artifacts with chunk metadata and provenance.
4. User feeds those outputs into an LLM, RAG pipeline, or agent workflow.

## Proposed Repository Shape

```text
github-star-index/
├── pyproject.toml
├── src/star_index/
│   ├── cli.py
│   ├── config.py
│   ├── auth.py
│   ├── models.py
│   ├── github_api.py
│   ├── categorize.py
│   ├── manifest.py
│   ├── diffing.py
│   ├── build/
│   │   ├── xml_writer.py
│   │   ├── summary_writer.py
│   │   └── raw_writer.py
│   ├── enrich/
│   │   └── readme.py
│   └── bundle/
│       ├── jsonl_writer.py
│       ├── markdown_writer.py
│       └── chunking.py
├── tests/
├── fixtures/
├── openspec/
└── examples/
```

The existing script files can remain as thin wrappers during migration, but the package becomes the source of truth.

## CLI Surface

The package SHOULD expose one executable, `star-index`, with subcommands:

- `build` - fetch and generate the primary artifacts
- `refresh` - rebuild and produce a diff report
- `bundle` - generate LLM-ready bundle artifacts from cached normalized data
- `validate` - confirm artifact consistency and schema expectations
- `fetch` - optional low-level fetch/cache step if we decide to separate fetch from build

The initial implementation can alias existing workflows while the package refactor is underway. The CLI must not require editing source defaults.

## Data Model

The tool should standardize on a normalized repository record used across all writers.

Core fields:
- repository identity: `id`, `node_id`, `full_name`, `owner`, `html_url`
- fetch metadata: `starred_at`, `fetched_at`, `source_user`
- repository metadata: `description`, `homepage`, `language`, `topics`, `license`, `archived`, `fork`, `default_branch`
- metrics: `stargazers_count`, `forks_count`, `watchers_count`, `open_issues_count`
- classification: inferred categories, manual categories, `llm_use`
- provenance: where each category or enrichment came from

Normalized data should be written to a stable JSON artifact that downstream commands can consume without refetching.

## Artifact Model

### Existing primary artifacts
- raw JSON fetch cache
- XML index
- Markdown summary
- Markdown refresh diff report

### New required artifacts
- `manifest.json`: machine-readable inventory of generated artifacts, versions, counts, and provenance
- `corpus/repos.jsonl`: one agent-ready record per repository
- `corpus/chunks.jsonl`: chunked records for retrieval or long-context batching
- `corpus/categories.jsonl`: category-level or thematic rollups

Optional after `0.1.0`:
- `snapshots/readmes/<owner>__<repo>.md`
- `corpus/readme-chunks.jsonl`

The manifest is the coordination layer. It lets agents discover what exists instead of inferring filenames from convention.

## Bundle Strategy

The core differentiator is not XML export alone. It is the bundle layer.

Each bundle record should contain:
- stable id
- source repository reference
- artifact type
- text payload
- chunk order and total count
- category labels
- timestamps
- provenance fields identifying whether content came from GitHub metadata, inferred taxonomy, manual taxonomy, or README snapshot

This supports deterministic downstream use:
- prompt packing
- retrieval indexing
- agent memory imports
- offline analysis pipelines

## README Enrichment

README enrichment is out of scope for the first OSS release and remains a post-`0.1.0` extension point.

If added later:
- only fetch README content for repositories included in the normalized cache
- store snapshots locally with fetch timestamps
- mark enriched fields with provenance
- do not make README fetching a prerequisite for primary artifact generation

This keeps the initial release narrow while preserving a path to stronger agent corpora later.

## Configuration

Configuration should be available from:
1. CLI flags
2. environment variables
3. an optional project config file

Potential config fields:
- source GitHub user
- output directory
- enabled artifact types
- bundle profiles
- README enrichment toggle
- category override file path
- rate limit policy and retry policy

CLI flags should override config file values.

## Authentication and Rate Limits

Auth precedence:
1. `GH_TOKEN`
2. `GITHUB_TOKEN`
3. `gh auth token`
4. anonymous requests

Requirements:
- never persist token values in generated artifacts
- emit actionable rate-limit errors
- include enough context in logs and reports to explain why a fetch failed

## Testing Strategy

Tests should move from ad hoc runtime checks to fixture-driven verification:

- unit tests for normalization, categorization, manifest generation, and diff logic
- golden-file tests for XML, summary, manifest, and JSONL bundle output
- CLI smoke tests using fixture data and offline mode
- one authenticated integration path documented but not required in CI

Fixtures should be synthetic or public-sample based, never personal workspace outputs.

## OSS Readiness

The repo should include:
- package metadata (`pyproject.toml`)
- license
- contributing guidance
- example config
- sample outputs built from fixtures
- CI that runs lint, tests, and artifact validation

Generated personal `data/` should not be the repository demo path. Examples should use fixture-based sample artifacts.

## Migration Plan

### Phase 1
Keep current scripts working while introducing package modules.

### Phase 2
Move command entrypoints to the package and leave wrapper scripts only if they reduce migration friction.

### Phase 3
Update docs, examples, and automation to use `star-index ...` instead of direct script paths.

## Alternatives Considered

### Alternative: Compete on embeddings and semantic search
Rejected for v1. That space is crowded and would make the project harder to explain. The deterministic artifact wedge is cleaner.

### Alternative: Keep the project as a private script collection
Rejected because the current code already has product potential, but only if we package and narrow the promise.

### Alternative: Build a browser UI first
Rejected because it increases scope before we have a defensible engine.

## Open Questions
- Whether `fetch` should exist as a first-class command or remain internal.
