# github-star-index

Build deterministic, agent-ready knowledge artifacts from GitHub stars.

This repo is intentionally not a stars browser or hosted organizer. It is a local-first corpus builder for agents, long-context LLMs, and automation workflows.

This repository ships the tooling only. Keep live star caches and personal generated datasets in local, untracked output directories.

Package name: `github-star-index`  
CLI: `star-index`

## Current Scope

- fetch GitHub stars using `GH_TOKEN`, `GITHUB_TOKEN`, `gh auth token`, or anonymous requests
- build raw JSON, XML, Markdown summary, and manifest artifacts
- refresh and diff the local cache
- generate repository, chunked, and category-rollup JSONL bundles for agent ingestion
- rebuild from cached raw JSON in offline mode

## Commands

From the repo without installing:

```bash
PYTHONPATH=src python3 -m star_index build --user <github-user>
PYTHONPATH=src python3 -m star_index refresh --user <github-user>
PYTHONPATH=src python3 -m star_index bundle --user <github-user>
PYTHONPATH=src python3 -m star_index validate --user <github-user>
```

After install:

```bash
pip install -e .
star-index build --user <github-user>
```

Compatibility wrappers remain available:

```bash
python3 scripts/build_star_index.py --user <github-user>
python3 scripts/refresh_star_index.py --user <github-user>
```

Shared local verification:

```bash
bash scripts/run-checks.sh
```

## Artifacts

By default the tool writes:

- `data/<user>-stars.raw.json`
- `data/<user>-stars.xml`
- `data/<user>-stars.summary.md`
- `data/<user>-stars.manifest.json`
- `data/<user>-stars.last-refresh.md`
- `data/<user>-stars.last-refresh.json`
- `data/<user>-corpus/repos.jsonl`
- `data/<user>-corpus/chunks.jsonl`
- `data/<user>-corpus/categories.jsonl`
- `data/<user>-corpus/bundle.manifest.json`

## Public-Safe Examples

Fixture-derived sample outputs live in [`examples/sample-output/`](examples/sample-output/). Regenerate them with:

```bash
python3 scripts/generate_examples.py
```

## Manual Categories

Edit [`config/manual_categories.json`](config/manual_categories.json) to add repository-specific or topic-specific category overrides.

## Contributing

Contributor workflow is documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Automation

Packaged automation examples live in [`docs/AUTOMATION.md`](docs/AUTOMATION.md).

## Release

The current public-release checklist lives in [`docs/RELEASE.md`](docs/RELEASE.md).

## Positioning

The product wedge and `0.1.0` scope decisions live in [`docs/POSITIONING.md`](docs/POSITIONING.md).

## OpenSpec

The OSS differentiation plan lives under [`openspec/`](openspec/), with the active change at [`openspec/changes/agent-ready-oss-corpus/`](openspec/changes/agent-ready-oss-corpus/).

## Status

This workspace is the public/product branch of the idea. The operational local copy remains separate.
