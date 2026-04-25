from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from star_index import bundle as bundle_cmd
from star_index import build as build_cmd
from star_index import validate as validate_cmd


FIXTURE = Path(__file__).parent / "fixtures" / "sample-stars.raw.json"


class OfflineArtifactTests(unittest.TestCase):
    def test_offline_build_bundle_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "data"
            output_dir.mkdir()

            xml_path = output_dir / "sample-user-stars.xml"
            summary_path = output_dir / "sample-user-stars.summary.md"
            manifest_path = output_dir / "sample-user-stars.manifest.json"

            rc = build_cmd.main(
                [
                    "--offline",
                    "--raw-json",
                    str(FIXTURE),
                    "--xml",
                    str(xml_path),
                    "--summary",
                    str(summary_path),
                    "--manifest",
                    str(manifest_path),
                    "--manual-categories",
                    str(root / "missing-manual-categories.json"),
                ]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(xml_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertTrue(manifest_path.exists())

            root_xml = ET.parse(xml_path).getroot()
            self.assertEqual(len(root_xml.findall("./repositories/repository")), 2)

            bundle_dir = output_dir / "corpus"
            rc = bundle_cmd.main(
                [
                    "--raw-json",
                    str(FIXTURE),
                    "--bundle-dir",
                    str(bundle_dir),
                    "--manual-categories",
                    str(root / "missing-manual-categories.json"),
                ]
            )
            self.assertEqual(rc, 0)
            bundle_path = bundle_dir / "repos.jsonl"
            chunk_path = bundle_dir / "chunks.jsonl"
            category_path = bundle_dir / "categories.jsonl"
            bundle_manifest = bundle_dir / "bundle.manifest.json"
            self.assertTrue(bundle_path.exists())
            self.assertTrue(chunk_path.exists())
            self.assertTrue(category_path.exists())
            self.assertTrue(bundle_manifest.exists())

            lines = bundle_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            first_record = json.loads(lines[0])
            self.assertEqual(first_record["record_type"], "repository")
            self.assertIn("categories", first_record)

            rc = validate_cmd.main(
                [
                    "--xml",
                    str(xml_path),
                    "--raw-json",
                    str(FIXTURE),
                    "--summary",
                    str(summary_path),
                    "--manifest",
                    str(manifest_path),
                    "--bundle-dir",
                    str(bundle_dir),
                ]
            )
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
