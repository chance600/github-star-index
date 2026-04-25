# Tasks

## 1. Baseline and packaging
- [x] 1.1 Add package metadata and choose the distributable package name.
- [x] 1.2 Introduce `src/` package layout and move current script logic into importable modules.
- [x] 1.3 Add a CLI entrypoint with explicit subcommands for build, refresh, bundle, and validate.
- [x] 1.4 Remove hardcoded personal defaults from runtime behavior and document the new config precedence.

## 2. Normalize artifact generation
- [x] 2.1 Define the normalized repository record used by all writers.
- [x] 2.2 Refactor XML, raw JSON, and Markdown summary generation to consume the normalized model.
- [x] 2.3 Add `manifest.json` describing generated artifacts, counts, schema version, and provenance summary.
- [x] 2.4 Add validation checks that ensure XML, raw cache, summary, and manifest counts agree.

## 3. Build the agent-ready bundle layer
- [x] 3.1 Add `bundle` outputs for per-repository JSONL records.
- [x] 3.2 Add chunked bundle outputs for long-context and retrieval workflows.
- [x] 3.3 Add category rollup bundle outputs.
- [x] 3.4 Include provenance metadata for each bundle record.
- [x] 3.5 Decide whether README enrichment is in-scope for the first public release; if yes, implement it behind an explicit flag.

## 4. Refresh and diff hardening
- [x] 4.1 Move refresh diff logic into package modules.
- [x] 4.2 Add machine-readable diff output or manifest pointers so automations can consume refresh results without parsing Markdown only.
- [x] 4.3 Ensure refresh reports remain human-readable and stable for inbox summaries.

## 5. OSS readiness
- [x] 5.1 Add synthetic or public-safe fixtures and sample outputs.
- [x] 5.2 Add tests for normalization, categorization, diffing, manifest generation, and bundle generation.
- [x] 5.3 Add CI for test and artifact validation.
- [x] 5.4 Add license, contributing guide, and publish-ready README examples.
- [x] 5.5 Stop relying on personal generated `data/` artifacts as the public demo path.

## 6. Release preparation
- [x] 6.1 Cut the first public-ready release checklist.
- [x] 6.2 Validate install-from-scratch on a clean environment.
- [x] 6.3 Update automation examples to use the packaged CLI instead of raw script paths.
- [x] 6.4 Reassess differentiation after the bundle layer is complete and tighten positioning before publication.
