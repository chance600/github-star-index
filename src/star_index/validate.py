from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .corpus import load_jsonl
from .paths import default_output_paths


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate star-index artifacts.")
    parser.add_argument("--user", help="GitHub username used to resolve default paths.")
    parser.add_argument("--output-dir", type=Path, default=Path("data"), help="Directory for generated artifacts.")
    parser.add_argument("--xml", type=Path, help="XML output path override.")
    parser.add_argument("--raw-json", type=Path, help="Raw JSON cache path override.")
    parser.add_argument("--summary", type=Path, help="Markdown summary path override.")
    parser.add_argument("--manifest", type=Path, help="Manifest path override.")
    parser.add_argument("--bundle-dir", type=Path, help="Bundle directory override.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    defaults = default_output_paths(args.user, args.output_dir)
    xml_path = args.xml or defaults["xml"]
    raw_json = args.raw_json or defaults["raw_json"]
    summary_path = args.summary or defaults["summary"]
    manifest_path = args.manifest or defaults["manifest"]
    bundle_dir = args.bundle_dir

    root = ET.parse(xml_path).getroot()
    with raw_json.open("r", encoding="utf-8") as handle:
        raw_payload = json.load(handle)
    summary_text = summary_path.read_text(encoding="utf-8")
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    xml_count = len(root.findall("./repositories/repository"))
    raw_count = len(raw_payload.get("stars", []))
    manifest_count = int(manifest.get("repository_count", -1))
    summary_match = re.search(r"- Repositories: `(\d+)`", summary_text)
    summary_count = int(summary_match.group(1)) if summary_match else -1

    if xml_count != raw_count or xml_count != manifest_count or xml_count != summary_count:
        raise SystemExit(
            "Artifact count mismatch: "
            f"xml={xml_count}, raw_json={raw_count}, summary={summary_count}, manifest={manifest_count}"
        )

    if bundle_dir:
        repo_bundle = bundle_dir / "repos.jsonl"
        chunk_bundle = bundle_dir / "chunks.jsonl"
        category_bundle = bundle_dir / "categories.jsonl"
        bundle_manifest_path = bundle_dir / "bundle.manifest.json"
        repo_records = load_jsonl(repo_bundle)
        chunk_records = load_jsonl(chunk_bundle)
        category_records = load_jsonl(category_bundle)
        with bundle_manifest_path.open("r", encoding="utf-8") as handle:
            bundle_manifest = json.load(handle)
        if len(repo_records) != raw_count:
            raise SystemExit(f"Bundle repository count mismatch: repos.jsonl={len(repo_records)}, raw_json={raw_count}")
        if len(chunk_records) < raw_count:
            raise SystemExit(f"Bundle chunk count too small: chunks.jsonl={len(chunk_records)}, raw_json={raw_count}")
        if len(category_records) != int(bundle_manifest.get("category_count", -1)):
            raise SystemExit(
                f"Bundle category count mismatch: categories.jsonl={len(category_records)}, "
                f"bundle_manifest={bundle_manifest.get('category_count', -1)}"
            )
        if len(repo_records) != int(bundle_manifest.get("repository_count", -1)):
            raise SystemExit(
                f"Bundle repository count mismatch: repos.jsonl={len(repo_records)}, "
                f"bundle_manifest={bundle_manifest.get('repository_count', -1)}"
            )
        if len(chunk_records) != int(bundle_manifest.get("chunk_count", -1)):
            raise SystemExit(
                f"Bundle chunk count mismatch: chunks.jsonl={len(chunk_records)}, "
                f"bundle_manifest={bundle_manifest.get('chunk_count', -1)}"
            )

    print(f"Validated artifacts: {xml_count} repositories")
    return 0
