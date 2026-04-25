from __future__ import annotations

from pathlib import Path


DEFAULT_CONFIG_PATH = Path("config/manual_categories.json")


def artifact_prefix(user: str | None) -> str:
    return user or "github-stars"


def default_output_paths(user: str | None, output_dir: Path) -> dict[str, Path]:
    prefix = artifact_prefix(user)
    return {
        "xml": output_dir / f"{prefix}-stars.xml",
        "raw_json": output_dir / f"{prefix}-stars.raw.json",
        "summary": output_dir / f"{prefix}-stars.summary.md",
        "report": output_dir / f"{prefix}-stars.last-refresh.md",
        "report_json": output_dir / f"{prefix}-stars.last-refresh.json",
        "manifest": output_dir / f"{prefix}-stars.manifest.json",
        "bundle_dir": output_dir / f"{prefix}-corpus",
    }
