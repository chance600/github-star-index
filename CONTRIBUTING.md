# Contributing

## Scope

This repository is the OSS/package track for `star-index`. It stays separate from any live personal star cache or private automation workspace.

## Development Loop

1. Create or update public-safe fixtures under `tests/fixtures/`.
2. Implement changes under `src/star_index/`.
3. Regenerate example artifacts:

```bash
python3 scripts/generate_examples.py
```

4. Run the shared verification wrapper:

```bash
bash scripts/run-checks.sh
```

## Guardrails

- Do not commit personal generated `data/` outputs.
- Keep example artifacts derived from fixtures only.
- Keep network access out of tests and CI.
- Prefer extending normalized artifact writers over adding source-specific heuristics.
