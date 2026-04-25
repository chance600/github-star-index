from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import load_raw_json
from .corpus import category_rollup_records, chunk_records, repository_record, write_bundle_manifest, write_jsonl
from .github_api import normalize_star_items
from .paths import DEFAULT_CONFIG_PATH, default_output_paths
from .taxonomy import categorize_repositories, load_manual_categories


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build agent-ready JSONL bundle artifacts from cached star data.")
    parser.add_argument("--user", help="GitHub username used to resolve default output paths.")
    parser.add_argument("--output-dir", type=Path, default=Path("data"), help="Directory for generated artifacts.")
    parser.add_argument("--raw-json", type=Path, help="Raw JSON cache path override.")
    parser.add_argument("--bundle-dir", type=Path, help="Bundle directory override.")
    parser.add_argument("--manifest", type=Path, help="Bundle manifest path override.")
    parser.add_argument("--manual-categories", type=Path, default=DEFAULT_CONFIG_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    defaults = default_output_paths(args.user, args.output_dir)
    raw_json = args.raw_json or defaults["raw_json"]
    bundle_dir = args.bundle_dir or defaults["bundle_dir"]
    bundle_manifest = args.manifest or bundle_dir / "bundle.manifest.json"

    source_user, stars, _, generated_at = load_raw_json(raw_json)
    repos = normalize_star_items(stars)
    manual = load_manual_categories(args.manual_categories)
    category_by_repo = categorize_repositories(repos, manual)
    repo_records = [
        repository_record(
            repo,
            categories=category_by_repo[repo.get("full_name") or ""],
            source_user=source_user,
            generated_at=generated_at,
        )
        for repo in repos
    ]
    chunked_records = [
        chunk
        for repo in repos
        for chunk in chunk_records(
            repo,
            categories=category_by_repo[repo.get("full_name") or ""],
            source_user=source_user,
            generated_at=generated_at,
        )
    ]
    category_records = category_rollup_records(
        repos,
        category_by_repo=category_by_repo,
        source_user=source_user,
        generated_at=generated_at,
    )

    repo_path = bundle_dir / "repos.jsonl"
    chunk_path = bundle_dir / "chunks.jsonl"
    category_path = bundle_dir / "categories.jsonl"
    write_jsonl(repo_path, repo_records)
    write_jsonl(chunk_path, chunked_records)
    write_jsonl(category_path, category_records)
    write_bundle_manifest(
        bundle_manifest,
        source_user=source_user,
        generated_at=generated_at,
        repository_count=len(repo_records),
        chunk_count=len(chunked_records),
        category_count=len(category_records),
        artifacts={
            "repositories": repo_path,
            "chunks": chunk_path,
            "categories": category_path,
        },
    )
    print(f"Wrote {repo_path} ({len(repo_records)} repository records)")
    print(f"Wrote {chunk_path} ({len(chunked_records)} chunk records)")
    print(f"Wrote {category_path} ({len(category_records)} category records)")
    print(f"Wrote {bundle_manifest}")
    return 0
