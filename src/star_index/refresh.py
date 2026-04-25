#!/usr/bin/env python3
"""Refresh the star index and write a change report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .build import resolve_user, run_build, utc_now
from .diffing import compute_repo_diff, write_refresh_json, write_refresh_markdown
from .paths import DEFAULT_CONFIG_PATH, default_output_paths


def load_repos(raw_json: Path) -> dict[str, dict[str, Any]]:
    if not raw_json.exists():
        return {}
    with raw_json.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    repos: dict[str, dict[str, Any]] = {}
    for item in payload.get("stars", []):
        repo = item.get("repo", item)
        full_name = repo.get("full_name")
        if not full_name:
            continue
        repos[full_name] = {
            "full_name": full_name,
            "html_url": repo.get("html_url"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "starred_at": item.get("starred_at") or repo.get("starred_at"),
        }
    return repos


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh the star index and write a change report.")
    parser.add_argument("--user", help="GitHub username whose stars should be indexed.")
    parser.add_argument("--output-dir", type=Path, default=Path("data"), help="Directory for generated artifacts.")
    parser.add_argument("--xml", type=Path, help="XML output path override.")
    parser.add_argument("--raw-json", type=Path, help="Raw JSON cache path override.")
    parser.add_argument("--summary", type=Path, help="Markdown summary path override.")
    parser.add_argument("--manifest", type=Path, help="Manifest JSON path override.")
    parser.add_argument("--report", type=Path, help="Refresh report path override.")
    parser.add_argument("--report-json", type=Path, help="Machine-readable refresh diff path override.")
    parser.add_argument("--manual-categories", type=Path, default=DEFAULT_CONFIG_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    initial_defaults = default_output_paths(args.user, args.output_dir)
    raw_json = args.raw_json or initial_defaults["raw_json"]
    before = load_repos(raw_json)
    user = resolve_user(args.user, raw_json.exists(), raw_json)
    defaults = default_output_paths(user, args.output_dir)

    result = run_build(
        user=user,
        xml_path=args.xml or defaults["xml"],
        raw_json_path=raw_json,
        summary_path=args.summary or defaults["summary"],
        manifest_path=args.manifest or defaults["manifest"],
        manual_categories_path=args.manual_categories,
        offline=False,
    )

    after = load_repos(raw_json)
    report_path = args.report or defaults["report"]
    report_json_path = args.report_json or defaults["report_json"]
    refreshed_at = utc_now()
    diff = compute_repo_diff(before, after)
    write_refresh_markdown(report_path, diff=diff, user=result["user"], refreshed_at=refreshed_at)
    write_refresh_json(
        report_json_path,
        diff=diff,
        user=result["user"],
        refreshed_at=refreshed_at,
        raw_json_path=raw_json,
        report_path=report_path,
    )
    print(f"Wrote {report_path}")
    print(f"Wrote {report_json_path}")
    print(f"Repository count: {diff['before_count']} -> {diff['after_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
