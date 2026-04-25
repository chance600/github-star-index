# Automation

The packaged CLI is the supported automation surface.

## Cron

Daily refresh and bundle rebuild:

```bash
star-index refresh --user <github-user> --output-dir /path/to/data
star-index bundle --user <github-user> --output-dir /path/to/data
star-index validate --user <github-user> --output-dir /path/to/data --bundle-dir /path/to/data/<github-user>-corpus
```

Example cron entry:

```cron
0 7 * * * cd /path/to/star-index && .venv/bin/star-index refresh --user <github-user> --output-dir /path/to/data && .venv/bin/star-index bundle --user <github-user> --output-dir /path/to/data && .venv/bin/star-index validate --user <github-user> --output-dir /path/to/data --bundle-dir /path/to/data/<github-user>-corpus
```

## GitHub Actions

For public-safe CI, use fixture-based verification via [`scripts/run-checks.sh`](../scripts/run-checks.sh).

For a private scheduled refresh workflow, install the package in the runner, set `GH_TOKEN`, and invoke the same packaged commands shown above.
