# Verification

## Current Entry Point

```bash
bash scripts/run-checks.sh
```

## Coverage

- Python syntax compilation for `src/`, `scripts/`, and `tests/`
- Offline unit tests from synthetic fixtures
- Fixture-driven example generation
- Artifact validation for XML, raw JSON, summary, manifest, and bundle outputs
- OpenSpec validation when `openspec` is installed
- Packaged CLI validation from a fresh venv using `pip install --no-build-isolation -e .`
