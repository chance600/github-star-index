from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from star_index.diffing import compute_repo_diff, write_refresh_json, write_refresh_markdown


class RefreshDiffTests(unittest.TestCase):
    def test_refresh_diff_writes_markdown_and_json(self) -> None:
        before = {
            "example/alpha": {
                "full_name": "example/alpha",
                "html_url": "https://github.com/example/alpha",
                "language": "Python",
                "stars": 10,
            }
        }
        after = {
            "example/beta": {
                "full_name": "example/beta",
                "html_url": "https://github.com/example/beta",
                "language": "TypeScript",
                "stars": 15,
            }
        }
        diff = compute_repo_diff(before, after)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            report_md = root / "refresh.md"
            report_json = root / "refresh.json"
            raw_json = root / "sample.raw.json"
            raw_json.write_text("{}", encoding="utf-8")

            write_refresh_markdown(report_md, diff=diff, user="sample-user", refreshed_at="2026-04-24T00:00:00+00:00")
            write_refresh_json(
                report_json,
                diff=diff,
                user="sample-user",
                refreshed_at="2026-04-24T00:00:00+00:00",
                raw_json_path=raw_json,
                report_path=report_md,
            )

            markdown = report_md.read_text(encoding="utf-8")
            payload = json.loads(report_json.read_text(encoding="utf-8"))

            self.assertIn("Added Repositories", markdown)
            self.assertIn("example/beta", markdown)
            self.assertEqual(payload["before_count"], 1)
            self.assertEqual(payload["after_count"], 1)
            self.assertEqual(payload["added"][0]["full_name"], "example/beta")
            self.assertEqual(payload["removed"][0]["full_name"], "example/alpha")


if __name__ == "__main__":
    unittest.main()
