#!/usr/bin/env python3

from __future__ import annotations

import shutil
import sys
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from star_index import build as build_cmd
from star_index import bundle as bundle_cmd
from star_index import validate as validate_cmd
from star_index.diffing import compute_repo_diff, write_refresh_json, write_refresh_markdown
from star_index.refresh import load_repos


FIXTURE = Path("tests/fixtures/sample-stars.raw.json")
BEFORE_FIXTURE = Path("tests/fixtures/sample-stars-before.raw.json")
OUTPUT_DIR = Path("examples/sample-output")
BUNDLE_DIR = OUTPUT_DIR / "corpus"
RAW_JSON = OUTPUT_DIR / "sample-user-stars.raw.json"
XML = OUTPUT_DIR / "sample-user-stars.xml"
SUMMARY = OUTPUT_DIR / "sample-user-stars.summary.md"
MANIFEST = OUTPUT_DIR / "sample-user-stars.manifest.json"
REPORT_MD = OUTPUT_DIR / "sample-user-stars.last-refresh.md"
REPORT_JSON = OUTPUT_DIR / "sample-user-stars.last-refresh.json"


def main() -> int:
    os.chdir(ROOT)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURE, RAW_JSON)

    rc = build_cmd.main(
        [
            "--offline",
            "--raw-json",
            str(RAW_JSON),
            "--xml",
            str(XML),
            "--summary",
            str(SUMMARY),
            "--manifest",
            str(MANIFEST),
            "--manual-categories",
            "config/manual_categories.json",
        ]
    )
    if rc != 0:
        return rc

    rc = bundle_cmd.main(
        [
            "--raw-json",
            str(RAW_JSON),
            "--bundle-dir",
            str(BUNDLE_DIR),
            "--manual-categories",
            "config/manual_categories.json",
        ]
    )
    if rc != 0:
        return rc

    diff = compute_repo_diff(load_repos(BEFORE_FIXTURE), load_repos(RAW_JSON))
    write_refresh_markdown(REPORT_MD, diff=diff, user="sample-user", refreshed_at="2026-04-24T00:00:00+00:00")
    write_refresh_json(
        REPORT_JSON,
        diff=diff,
        user="sample-user",
        refreshed_at="2026-04-24T00:00:00+00:00",
        raw_json_path=RAW_JSON,
        report_path=REPORT_MD,
    )

    return validate_cmd.main(
        [
            "--xml",
            str(XML),
            "--raw-json",
            str(RAW_JSON),
            "--summary",
            str(SUMMARY),
            "--manifest",
            str(MANIFEST),
            "--bundle-dir",
            str(BUNDLE_DIR),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
