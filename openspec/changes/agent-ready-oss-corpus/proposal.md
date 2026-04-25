# Proposal: Ship star-index as an agent-ready OSS corpus builder

## Intent
Turn `github-star-index` from a personal export script into an installable open source tool with a clear wedge: deterministic, local-first, agent-ready corpus generation from GitHub stars.

## Problem
The current project works for one operator and one repository layout, but it is not yet a credible open source product:

- the code is script-shaped instead of package-shaped
- the CLI contract is implicit and partially hardcoded to `chance600`
- the output is useful for a single long XML file, but not yet optimized as a reusable corpus for agents and retrieval pipelines
- the repository still reads as a personal workspace artifact rather than a distributable tool

There are already tools that organize, search, or semantically classify GitHub stars. If this project is open sourced in its current form, it will look like a cleaner exporter, not a materially different product.

## Product Wedge
The project will differentiate on deterministic artifact generation rather than hosted search or opaque LLM classification.

Positioning:

> Build agent-ready knowledge artifacts from GitHub stars.

The v1 open source promise is:

- local-first operation
- deterministic outputs
- provenance-rich artifacts
- installable CLI
- no required embedding service or hosted backend
- refresh and diff workflow suitable for recurring automation

## Scope
In scope for this change:

- refactor scripts into an installable CLI package
- support explicit subcommands for fetch/build/bundle/refresh/validate
- keep XML/JSON/Markdown outputs and add a machine-readable manifest
- add corpus bundle outputs designed for LLM ingestion
- keep README snapshot enrichment out of scope for `0.1.0`
- replace hardcoded personal defaults with config and CLI flags
- add tests, fixtures, packaging metadata, license, and CI suitable for open source publication

Out of scope for this change:

- hosted SaaS or multi-user backend
- vector database integration
- automatic write-back to GitHub Lists
- paid cloud enrichment services
- a frontend application or dashboard

## Approach
Deliver the change as a brownfield OpenSpec change with these implementation phases:

1. Establish the package and CLI surface.
2. Separate fetch/build/bundle/refresh concerns into modules with stable data contracts.
3. Add manifest and corpus bundle outputs so the tool becomes useful to agents, not only humans.
4. Add OSS hygiene: tests, fixtures, docs, CI, and release metadata.

## Success Criteria
This change is successful when:

- a fresh user can install the project and run `star-index` without editing source code
- the tool can build the same primary artifacts as today from CLI flags or config
- the tool can emit a machine-readable corpus bundle with provenance and chunk metadata
- generated sample outputs no longer depend on private `chance600` data
- the repository reads as a reusable OSS package with docs, tests, and release scaffolding

## Risks
- README enrichment can expand scope quickly if it becomes a crawler instead of a targeted snapshot step.
- Artifact proliferation can make the tool confusing unless the manifest is explicit and the command surface stays small.
- Packaging and test cleanup can become busywork unless tied to the product wedge.

## Why Now
The project already proves the core GitHub fetch and refresh loop. The next step is to convert that working core into a product with a defensible difference before more implementation accumulates around personal assumptions.
