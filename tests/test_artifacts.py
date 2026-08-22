from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rpcd_harness.artifacts import (
    _is_excluded,
    _sensitive_content_kind,
    create_bundle,
    unpack_bundle,
    verify_bundle,
)
from rpcd_harness.protocol import find_root


class PortableBundleTests(unittest.TestCase):
    def test_nested_credentials_and_temporary_files_are_excluded(self) -> None:
        for relative in (
            Path("tmp/page.png"),
            Path("nested/.codex/auth.json"),
            Path("nested/.npmrc"),
            Path("nested/id_ed25519"),
            Path("nested/client.pem"),
        ):
            self.assertTrue(_is_excluded(relative, include_runs=False), relative)

    def test_high_confidence_secret_content_is_detected_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "notes.txt"
            candidate.write_text("ghp_" + "A" * 36, encoding="utf-8")
            self.assertEqual(_sensitive_content_kind(candidate), "github-token")

    def test_bundle_round_trip_and_credential_exclusion(self) -> None:
        root = find_root()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bundle = create_bundle(root, "T020-exact-small-n", directory / "packet.zip")
            manifest = verify_bundle(bundle)
            names = {entry["path"] for entry in manifest["files"]}
            self.assertIn("research/tasks/T020-exact-small-n.json", names)
            self.assertFalse(any("auth.json" in name or name.startswith(".codex/") for name in names))
            self.assertFalse(any(name.startswith("tmp/") for name in names))
            destination = directory / "unpacked"
            written = unpack_bundle(bundle, destination)
            self.assertGreater(len(written), 20)
            self.assertTrue((destination / "README.md").is_file())

    def test_include_runs_is_scoped_to_the_selected_task(self) -> None:
        root = find_root()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            selected = root / "runs" / "T020-exact-small-n" / "test-selected.txt"
            other = root / "runs" / "T030-counterexample-search" / "test-other.txt"
            try:
                selected.parent.mkdir(parents=True, exist_ok=True)
                other.parent.mkdir(parents=True, exist_ok=True)
                selected.write_text("selected", encoding="utf-8")
                other.write_text("other", encoding="utf-8")
                bundle = create_bundle(
                    root,
                    "T020-exact-small-n",
                    directory / "packet-with-runs.zip",
                    include_runs=True,
                )
                names = {entry["path"] for entry in verify_bundle(bundle)["files"]}
                self.assertIn(selected.relative_to(root).as_posix(), names)
                self.assertNotIn(other.relative_to(root).as_posix(), names)
            finally:
                selected.unlink(missing_ok=True)
                other.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
