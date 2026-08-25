from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rpcd_harness.verifiers import (
    _expand_command,
    _expanded_command_errors,
    run_verifier,
    run_verifiers,
    validate_verifier_spec,
)


def verifier_spec(command: list[str], **overrides: object) -> dict:
    spec = {
        "name": "exact RPCD identity",
        "command": command,
        "mode": "exact",
        "timeout_seconds": 10,
        "expected_exit_code": 0,
    }
    spec.update(overrides)
    return spec


class VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.artifact_dir = self.root / "runs" / "run-test" / "artifacts"
        self.run_dir = self.root / "runs" / "run-test"
        self.artifact_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_python_verifier_expands_placeholders_and_captures_streams(self) -> None:
        code = (
            "import pathlib,sys; "
            "print(pathlib.Path(sys.argv[1]).name); "
            "print(pathlib.Path(sys.argv[2]).name, file=sys.stderr)"
        )
        spec = verifier_spec(
            [sys.executable, "-c", code, "{artifact_dir}", "{root}"]
        )

        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )

        self.assertTrue(record["passed"], record["errors"])
        self.assertEqual(record["status"], "passed")
        self.assertEqual(record["exit_code"], 0)
        stdout = self.root / record["stdout_path"]
        stderr = self.root / record["stderr_path"]
        self.assertEqual(stdout.read_text(encoding="utf-8").strip(), "artifacts")
        self.assertEqual(stderr.read_text(encoding="utf-8").strip(), self.root.name)
        self.assertEqual(record["command"][-2], str(self.artifact_dir))
        self.assertEqual(record["stdout_bytes"], stdout.stat().st_size)
        self.assertEqual(
            record["stdout_sha256"], hashlib.sha256(stdout.read_bytes()).hexdigest()
        )

    def test_python_placeholder_uses_current_portable_interpreter(self) -> None:
        spec = verifier_spec(
            [
                "{python}",
                "-c",
                "x = {'rpcd': 'ok'}; print(x['rpcd'])",
            ]
        )
        self.assertEqual(validate_verifier_spec(spec), [])
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertTrue(record["passed"], record["errors"])
        self.assertEqual(Path(record["command"][0]).resolve(), Path(sys.executable).resolve())
        self.assertEqual(
            (self.root / record["stdout_path"]).read_text(encoding="utf-8").strip(),
            "ok",
        )

    def test_versioned_current_python_is_trusted_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="rpcd-python-runtime-", dir=self.root.parent
        ) as runtime:
            fake_python = Path(runtime) / "python3.12"
            fake_python.write_bytes(b"versioned current interpreter placeholder")
            with patch(
                "rpcd_harness.verifiers.sys.executable", str(fake_python)
            ):
                command = _expand_command(
                    ["{python}", "-c", "print('ok')"],
                    root=self.root,
                    artifact_dir=self.artifact_dir,
                )
                errors = _expanded_command_errors(
                    command,
                    root=self.root,
                    artifact_dir=self.artifact_dir,
                )

        self.assertEqual(command[0], str(fake_python.resolve()))
        self.assertEqual(errors, [])

    def test_python_placeholder_is_only_valid_as_executable(self) -> None:
        errors = validate_verifier_spec(
            verifier_spec([sys.executable, "script.py", "--python={python}"])
        )
        self.assertTrue(any("complete executable token" in item for item in errors))

    def test_python_source_is_opaque_to_harness_placeholders(self) -> None:
        spec = verifier_spec(
            ["{python}", "-c", "value = '{root}'; print(value)"]
        )
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertTrue(record["passed"], record["errors"])
        self.assertEqual(
            (self.root / record["stdout_path"]).read_text(encoding="utf-8").strip(),
            "{root}",
        )

    def test_expected_nonzero_exit_code_can_pass(self) -> None:
        spec = verifier_spec(
            [sys.executable, "-c", "raise SystemExit(7)"],
            expected_exit_code=7,
            mode="deterministic",
        )
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertTrue(record["passed"], record["errors"])
        self.assertEqual(record["exit_code"], 7)

    def test_unexpected_exit_is_structured_failure_with_logs(self) -> None:
        spec = verifier_spec(
            [sys.executable, "-c", "import sys; print('no'); sys.exit(3)"]
        )
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertFalse(record["passed"])
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["exit_code"], 3)
        self.assertTrue((self.root / record["stdout_path"]).is_file())
        self.assertIn("did not match expected", record["errors"][0])

    def test_timeout_is_structured_and_captures_logs(self) -> None:
        spec = verifier_spec(
            [
                sys.executable,
                "-c",
                "import time; print('starting', flush=True); time.sleep(5)",
            ],
            timeout_seconds=1,
            mode="numerical",
        )
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(record["status"], "timed_out")
        self.assertTrue(record["timed_out"])
        self.assertLess(record["duration_seconds"], 4)
        self.assertIn("starting", (self.root / record["stdout_path"]).read_text())

    def test_rejects_shell_executable_and_control_operator(self) -> None:
        shell_record = run_verifier(
            verifier_spec(["powershell", "-Command", "Write-Output ok"]),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(shell_record["status"], "invalid")
        self.assertTrue(any("shell executable" in item for item in shell_record["errors"]))

        errors = validate_verifier_spec(
            verifier_spec([sys.executable, "script.py", "&&", "other.py"])
        )
        self.assertTrue(any("shell control operator" in item for item in errors))

    def test_python_source_with_semicolon_is_not_mistaken_for_a_shell(self) -> None:
        spec = verifier_spec(
            [sys.executable, "-c", "x = {'route': 1}; print(x['route'])"]
        )
        self.assertEqual(validate_verifier_spec(spec), [])
        record = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertTrue(record["passed"], record["errors"])

    def test_rejects_unknown_or_malformed_placeholders(self) -> None:
        unknown = validate_verifier_spec(
            verifier_spec([sys.executable, "script.py", "{workspace}"])
        )
        malformed = validate_verifier_spec(
            verifier_spec([sys.executable, "script.py", "{artifact_dir"])
        )
        self.assertTrue(any("unsupported placeholders" in item for item in unknown))
        self.assertTrue(any("malformed" in item for item in malformed))

        complex_placeholder = validate_verifier_spec(
            verifier_spec([sys.executable, "script.py", "{root.parent}"])
        )
        self.assertTrue(
            any("unsupported placeholder syntax" in item for item in complex_placeholder)
        )

    def test_rejects_path_escape_in_argument_or_directories(self) -> None:
        traversal = run_verifier(
            verifier_spec([sys.executable, "../outside.py"]),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(traversal["status"], "invalid")
        self.assertTrue(any("parent-path traversal" in item for item in traversal["errors"]))

        outside = self.root.parent / "outside-artifacts"
        directory_escape = run_verifier(
            verifier_spec([sys.executable, "-c", "print('ok')"]),
            root=self.root,
            artifact_dir=outside,
            run_dir=self.run_dir,
        )
        self.assertEqual(directory_escape["status"], "invalid")
        self.assertTrue(any("artifact_dir" in item for item in directory_escape["errors"]))

    def test_rejects_unapproved_bare_executable(self) -> None:
        record = run_verifier(
            verifier_spec(["curl", "https://example.test"]),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(record["status"], "invalid")
        self.assertTrue(any("bare executable is not approved" in item for item in record["errors"]))

    def test_rejects_spoofed_external_python_executable(self) -> None:
        fake_python = self.root.parent / "python.exe"
        try:
            fake_python.write_bytes(b"not a trusted interpreter")
            record = run_verifier(
                verifier_spec([str(fake_python), "-c", "print('unsafe')"]),
                root=self.root,
                artifact_dir=self.artifact_dir,
                run_dir=self.run_dir,
            )
            self.assertEqual(record["status"], "invalid")
            self.assertTrue(
                any("external executable" in item for item in record["errors"])
            )
        finally:
            fake_python.unlink(missing_ok=True)

    def test_refuses_to_overwrite_preexisting_stream_log(self) -> None:
        logs = self.run_dir / "verifiers"
        logs.mkdir()
        existing = logs / "000-exact-RPCD-identity.stdout.log"
        existing.write_text("preserve", encoding="utf-8")
        record = run_verifier(
            verifier_spec(["{python}", "-c", "print('new')"]),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(record["status"], "invalid")
        self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")
        self.assertTrue(any("already exists" in item for item in record["errors"]))

    def test_non_object_spec_returns_an_invalid_record_instead_of_raising(self) -> None:
        record = run_verifier(
            "python verifier.py",
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(record["status"], "invalid")
        self.assertIn("must be an object", record["errors"][0])

    def test_static_schema_rejects_bool_integer_fields_and_unknown_mode(self) -> None:
        errors = validate_verifier_spec(
            verifier_spec(
                [sys.executable, "-c", "print('ok')"],
                timeout_seconds=True,
                expected_exit_code=False,
                mode="symbolic",
            )
        )
        self.assertTrue(any("timeout_seconds" in item for item in errors))
        self.assertTrue(any("expected_exit_code" in item for item in errors))
        self.assertTrue(any("mode" in item for item in errors))

    def test_when_defaults_to_final_and_rejects_invalid_values(self) -> None:
        base = verifier_spec(["{python}", "-c", "print('ok')"])
        self.assertEqual(validate_verifier_spec(base), [])
        for when in ("preflight", "final", "both"):
            with self.subTest(when=when):
                self.assertEqual(
                    validate_verifier_spec({**base, "when": when}), []
                )

        errors = validate_verifier_spec({**base, "when": "midflight"})
        self.assertTrue(any("when must be one of" in item for item in errors))

        schema_path = Path(__file__).parents[1] / "schemas" / "task.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        when_schema = schema["properties"]["verifiers"]["items"]["properties"]["when"]
        self.assertEqual(when_schema["enum"], ["preflight", "final", "both"])

    def test_default_final_phase_runs_only_applicable_verifiers(self) -> None:
        specs = [
            verifier_spec(
                ["{python}", "-c", "print('default-final')"],
                name="default final",
            ),
            verifier_spec(
                ["{python}", "-c", "print('explicit-final')"],
                name="explicit final",
                when="final",
            ),
            verifier_spec(
                ["{python}", "-c", "raise SystemExit(9)"],
                name="preflight only",
                when="preflight",
            ),
            verifier_spec(
                ["{python}", "-c", "print('both')"],
                name="both phases",
                when="both",
            ),
        ]
        records, errors = run_verifiers(
            specs,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )

        self.assertEqual(errors, [])
        self.assertEqual(
            [record["name"] for record in records],
            ["default final", "explicit final", "both phases"],
        )
        self.assertEqual(
            [record["when"] for record in records], ["final", "final", "both"]
        )
        self.assertTrue(all(record["phase"] == "final" for record in records))
        self.assertTrue(all(record["passed"] for record in records))

    def test_preflight_phase_runs_preflight_and_both_only(self) -> None:
        specs = [
            verifier_spec(
                ["{python}", "-c", "raise SystemExit(8)"],
                name="implicit final",
            ),
            verifier_spec(
                ["{python}", "-c", "print('preflight')"],
                name="preflight",
                when="preflight",
            ),
            verifier_spec(
                ["{python}", "-c", "print('both')"],
                name="both",
                when="both",
            ),
        ]
        records, errors = run_verifiers(
            specs,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
            phase="preflight",
        )

        self.assertEqual(errors, [])
        self.assertEqual(
            [record["name"] for record in records], ["preflight", "both"]
        )
        self.assertEqual(
            [record["when"] for record in records], ["preflight", "both"]
        )
        self.assertTrue(all(record["phase"] == "preflight" for record in records))
        self.assertTrue(all("preflight-" in record["stdout_path"] for record in records))

    def test_both_verifier_has_distinct_preflight_and_final_logs(self) -> None:
        spec = verifier_spec(
            ["{python}", "-c", "print('verified')"],
            name="two stage check",
            when="both",
        )
        preflight = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
            phase="preflight",
        )
        final = run_verifier(
            spec,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
            phase="final",
        )

        self.assertTrue(preflight["passed"], preflight["errors"])
        self.assertTrue(final["passed"], final["errors"])
        self.assertEqual(preflight["when"], "both")
        self.assertEqual(final["when"], "both")
        self.assertEqual(preflight["phase"], "preflight")
        self.assertEqual(final["phase"], "final")
        self.assertNotEqual(preflight["stdout_path"], final["stdout_path"])
        self.assertTrue((self.root / preflight["stdout_path"]).is_file())
        self.assertTrue((self.root / final["stdout_path"]).is_file())

    def test_direct_nonapplicable_verifier_is_skipped_without_logs(self) -> None:
        record = run_verifier(
            verifier_spec(
                ["{python}", "-c", "raise SystemExit(6)"],
                when="preflight",
            ),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )

        self.assertEqual(record["status"], "skipped")
        self.assertFalse(record["passed"])
        self.assertEqual(record["errors"], [])
        self.assertEqual(record["when"], "preflight")
        self.assertEqual(record["phase"], "final")
        self.assertFalse((self.run_dir / "verifiers").exists())

    def test_invalid_phase_and_when_are_structured_errors(self) -> None:
        invalid_when = run_verifier(
            verifier_spec(["{python}", "-c", "print('no')"], when="sometimes"),
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
            phase="preflight",
        )
        self.assertEqual(invalid_when["status"], "invalid")
        self.assertTrue(
            any("when must be one of" in item for item in invalid_when["errors"])
        )

        records, errors = run_verifiers(
            [verifier_spec(["{python}", "-c", "print('no')"])],
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
            phase="midflight",
        )
        self.assertEqual(records, [])
        self.assertEqual(errors, ["phase must be one of preflight, final"])

    def test_batch_returns_all_records_and_prefixed_errors(self) -> None:
        specs = [
            verifier_spec(
                [sys.executable, "-c", "print('formal ok')"],
                name="lean lemma",
                mode="formal",
            ),
            verifier_spec(
                [sys.executable, "-c", "raise SystemExit(4)"],
                name="numerical regression",
                mode="numerical",
            ),
        ]
        records, errors = run_verifiers(
            specs,
            root=self.root,
            artifact_dir=self.artifact_dir,
            run_dir=self.run_dir,
        )
        self.assertEqual(len(records), 2)
        self.assertTrue(records[0]["passed"])
        self.assertFalse(records[1]["passed"])
        self.assertEqual(len(errors), 1)
        self.assertIn("verifier numerical regression", errors[0])


if __name__ == "__main__":
    unittest.main()
