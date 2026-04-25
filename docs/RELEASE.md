# Release Checklist

## Before tagging `0.1.0`

- Verify [`bash scripts/run-checks.sh`](../scripts/run-checks.sh) passes locally.
- Confirm example artifacts under [`examples/sample-output/`](../examples/sample-output/) were regenerated from fixtures.
- Confirm no personal generated `data/` outputs are staged.
- Re-run packaged CLI validation from a clean venv.
- Confirm README positioning still matches the current feature set.
- Confirm the published identity remains `github-star-index` for the package/repo and `star-index` for the CLI.

## Notes

- In this environment, a Python `3.14` venv without system site packages did not include `setuptools`, so offline editable install validation required `--system-site-packages` plus `--no-build-isolation`.
- The package itself has no runtime dependencies.
