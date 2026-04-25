# Positioning

## What `star-index` is

`star-index` is a local-first CLI that turns GitHub stars into deterministic, agent-ready knowledge artifacts.

Core promise:

- fetch and cache GitHub star metadata
- generate XML, JSON, Markdown, and JSONL artifacts
- preserve provenance for inferred and manual taxonomy
- emit refresh diffs that automations can consume
- work without embeddings, a hosted backend, or mandatory LLM calls

## What it is not

It is not trying to be:

- a hosted GitHub stars manager
- a semantic search SaaS
- a vector database wrapper
- a browser UI for curating stars
- a GitHub Lists write-back tool in `0.1.0`

## Competitive framing

Adjacent tools already cover browsing, tagging, search, or embedding-heavy organization.

The OSS wedge here is narrower:

> Build durable, deterministic corpora from GitHub stars for agents, long-context LLMs, and offline automation.

That means the repo should emphasize:

- artifact contracts over UI
- reproducibility over opaque enrichment
- local cache and diff workflows over hosted sync
- public-safe fixtures and examples over personal demo data

## `0.1.0` Decisions

- README enrichment is out of scope for `0.1.0`.
- Embeddings and vector stores stay out of scope.
- GitHub write operations stay out of scope.
- The package should ship as a CLI-first tool with fixture-driven examples and CI.

## Release Claim

For the first public release, the README should be able to make this claim without stretching:

> `star-index` turns GitHub stars into deterministic XML, Markdown, manifest, refresh-diff, and JSONL corpus artifacts for agent and LLM workflows.
