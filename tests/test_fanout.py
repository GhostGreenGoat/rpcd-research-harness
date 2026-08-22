from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from rpcd_harness.cli import build_parser
from rpcd_harness.fanout import (
    merge_fanout_shards,
    run_fanout,
    validate_fanout_manifest,
)
from rpcd_harness.protocol import (
    ProtocolError,
    latest_completed_fanout,
    read_json,
    repository_source_snapshot,
    sha256_file,
    write_json,
)


class FanoutTests(unittest.TestCase):
    task_id = "T900-fanout-portability"

    def manifest(self) -> dict:
        return {
            "schema_version": "1.0",
            "task_id": self.task_id,
            "rollouts": [
                {
                    "rollout_id": "spectral",
                    "worker": "worker-a",
                    "method_family": "spectral",
                    "context_mode": "statement_only",
                    "objective": "Test a spectral block-power route.",
                    "required_controls": ["one non-normal exact family"],
                },
                {
                    "rollout_id": "operator",
                    "worker": "worker-b",
                    "method_family": "operator",
                    "context_mode": "statement_only",
                    "objective": "Test an invariant-cone operator route.",
                    "required_controls": ["one reachable-cone exact family"],
                },
            ],
        }

    def make_root(self, directory: str, *, sealed: bool = False) -> tuple[Path, Path]:
        root = Path(directory)
        (root / "research" / "tasks").mkdir(parents=True)
        (root / "research" / "fanouts").mkdir(parents=True)
        task = {
            "schema_version": "1.0",
            "task_id": self.task_id,
            "title": "fanout portability fixture",
            "role": "explorer",
            "objective": "exercise portable fanout lineage",
            "claim_ids": [],
            "dependencies": [],
            "inputs": [],
            "fanout_manifest": "research/fanouts/fixture.json",
            "allowed_max_evidence": "E3",
            "required_artifacts": [],
            "acceptance_checks": [],
            "verifiers": [
                {
                    "name": "fixture exact control",
                    "command": ["python", "fixture_control.py"],
                    "mode": "exact",
                    "timeout_seconds": 30,
                    "expected_exit_code": 0,
                    "when": "both",
                }
            ],
            "status": "ready",
        }
        if sealed:
            statement = root / "statement.md"
            statement.write_text("normalized statement\n", encoding="utf-8")
            task.update(
                {
                    "research_mode": "sealed_breadth",
                    "inputs": ["statement.md"],
                    "context_policy": {
                        "mode": "statement_only",
                        "allowlist": ["statement.md"],
                        "denylist": [],
                        "reveal_after_route_card": True,
                    },
                    "rollout_strategy": {
                        "route_card_minutes": 20,
                        "immutable_route_card": True,
                    },
                }
            )
        write_json(root / "research" / "tasks" / f"{self.task_id}.json", task)
        manifest_path = root / "research" / "fanouts" / "fixture.json"
        write_json(manifest_path, self.manifest())
        return root, manifest_path

    def completed_runner(self, root: Path, task_id: str, **kwargs) -> Path:
        strategy = kwargs["rollout_strategy"]
        run_id = f"run-{strategy['rollout_id']}"
        run_dir = root / "runs" / task_id / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        artifact_dir = run_dir / "artifacts"
        artifact_dir.mkdir()
        task = read_json(root / "research" / "tasks" / f"{task_id}.json")
        artifact = artifact_dir / "notes.md"
        artifact.write_text("portable evidence\n", encoding="utf-8")
        for raw in task.get("dynamic_verifier_artifacts", []):
            dynamic = artifact_dir / raw
            dynamic.parent.mkdir(parents=True, exist_ok=True)
            dynamic.write_text("print('dynamic verifier ok')\n", encoding="utf-8")
        write_json(run_dir / "task.json", task)

        verifier_dir = run_dir / "verifiers"
        verifier_dir.mkdir()

        def verifier_records(phase: str) -> list[dict]:
            records: list[dict] = []
            specs = [dict(spec) for spec in task.get("verifiers", [])]
            if phase == "final":
                for dynamic_index, raw in enumerate(
                    task.get("dynamic_verifier_artifacts", []), start=1
                ):
                    specs.append(
                        {
                            "name": f"agent-produced exact control {dynamic_index}: {raw}",
                            "command": ["{python}", f"{{artifact_dir}}/{raw}"],
                            "mode": "exact",
                            "timeout_seconds": 600,
                            "expected_exit_code": 0,
                            "when": "final",
                        }
                    )
            for index, spec in enumerate(specs):
                if spec.get("when", "final") not in {phase, "both"}:
                    continue
                prefix = "preflight-" if phase == "preflight" else "final-"
                stdout = verifier_dir / f"{index:03d}-{prefix}fixture.stdout.log"
                stderr = verifier_dir / f"{index:03d}-{prefix}fixture.stderr.log"
                stdout.write_text(f"{phase} ok\n", encoding="utf-8")
                stderr.write_bytes(b"")
                expanded_command = [
                    part.replace("{python}", str(Path(sys.executable).resolve()))
                    .replace("{root}", str(root.resolve()))
                    .replace("{artifact_dir}", str(artifact_dir.resolve()))
                    for part in spec["command"]
                ]
                records.append(
                    {
                        "schema_version": "1.0",
                        "index": index,
                        "name": spec["name"],
                        "mode": spec["mode"],
                        "when": spec.get("when", "final"),
                        "phase": phase,
                        "command": expanded_command,
                        "expected_exit_code": spec["expected_exit_code"],
                        "exit_code": spec["expected_exit_code"],
                        "status": "passed",
                        "passed": True,
                        "timed_out": False,
                        "duration_seconds": 0.01,
                        "started_at": "2026-08-22T00:00:00Z",
                        "finished_at": "2026-08-22T00:00:01Z",
                        "stdout_path": stdout.relative_to(root).as_posix(),
                        "stderr_path": stderr.relative_to(root).as_posix(),
                        "stdout_bytes": stdout.stat().st_size,
                        "stderr_bytes": stderr.stat().st_size,
                        "stdout_sha256": sha256_file(stdout),
                        "stderr_sha256": sha256_file(stderr),
                        "errors": [],
                    }
                )
            return records

        preflight_records = verifier_records("preflight")
        final_records = verifier_records("final")
        preflight_path = run_dir / "trusted_verifiers.preflight.json"
        write_json(
            preflight_path,
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "phase": "preflight",
                "status": "passed" if preflight_records else "not_configured",
                "records": preflight_records,
                "errors": [],
            },
        )
        write_json(
            run_dir / "trusted_verifiers.json",
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "records": final_records,
                "errors": [],
            },
        )
        write_json(
            run_dir / "invocation.json",
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "worker": strategy["worker"],
                "dry_run": False,
                "iteration_complete": True,
                "active_research_seconds": 7200.0,
                "exit_code": 0,
                "phases": [
                    {"phase": 1, "active_seconds": 7200.0, "exit_code": 0}
                ],
                "rollout_strategy": strategy,
                "repository_source_snapshot": repository_source_snapshot(root, task),
                "cwd": str(root.resolve()),
                "preflight_verifiers": {
                    "path": preflight_path.relative_to(root).as_posix(),
                    "status": "passed" if preflight_records else "not_configured",
                    "valid": True,
                },
            },
        )
        write_json(run_dir / "validation.json", {"valid": True, "errors": []})
        write_json(
            run_dir / "result.json",
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "worker": strategy["worker"],
                "artifacts": [
                    {"path": path.relative_to(root).as_posix()}
                    for path in sorted(artifact_dir.rglob("*"))
                    if path.is_file()
                ],
            },
        )
        write_json(
            run_dir / "artifact_manifest.json",
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "files": [
                    {
                        "path": path.relative_to(root).as_posix(),
                        "sha256": sha256_file(path),
                        "bytes": path.stat().st_size,
                    }
                    for path in sorted(artifact_dir.rglob("*"))
                    if path.is_file()
                ],
            },
        )
        return run_dir

    def dry_runner(self, root: Path, task_id: str, **kwargs) -> Path:
        rollout_id = kwargs["rollout_strategy"]["rollout_id"]
        run_dir = root / "runs" / task_id / f"dry-{rollout_id}"
        run_dir.mkdir(parents=True, exist_ok=False)
        return run_dir

    def make_shards(self, root: Path, manifest_path: Path) -> tuple[Path, Path]:
        spectral = run_fanout(
            root,
            self.task_id,
            manifest_path,
            rollout_ids=["spectral"],
            runner=self.completed_runner,
        )
        operator = run_fanout(
            root,
            self.task_id,
            manifest_path,
            rollout_ids=["operator"],
            runner=self.completed_runner,
        )
        return spectral, operator

    def test_duplicate_method_families_are_rejected(self) -> None:
        manifest = self.manifest()
        manifest["rollouts"][1]["method_family"] = " spectral "
        errors = validate_fanout_manifest(manifest, task_id=self.task_id)
        self.assertTrue(any("distinct method_family" in error for error in errors))

    def test_full_dry_fanout_is_complete_and_repository_relative(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            ensemble = run_fanout(
                root,
                self.task_id,
                manifest_path.relative_to(root),
                dry_run=True,
                runner=self.dry_runner,
            )
            value = read_json(ensemble)
            self.assertTrue(value["complete"])
            self.assertTrue(value["dry_run"])
            self.assertEqual(value["selected_rollout_ids"], ["spectral", "operator"])
            self.assertEqual(value["source_manifest"], "research/fanouts/fixture.json")
            self.assertTrue(
                all(not Path(record["run_dir"]).is_absolute() for record in value["rollouts"])
            )

    def test_rollout_id_is_repeatable_and_creates_an_incomplete_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            calls: list[str] = []

            def runner(root: Path, task_id: str, **kwargs) -> Path:
                calls.append(kwargs["rollout_strategy"]["rollout_id"])
                return self.dry_runner(root, task_id, **kwargs)

            ensemble = run_fanout(
                root,
                self.task_id,
                manifest_path,
                dry_run=True,
                rollout_ids=["operator"],
                runner=runner,
            )
            value = read_json(ensemble)
            self.assertFalse(value["complete"])
            self.assertEqual(value["selected_rollout_ids"], ["operator"])
            self.assertEqual(calls, ["operator"])
            with self.assertRaisesRegex(ProtocolError, "duplicates"):
                run_fanout(
                    root,
                    self.task_id,
                    manifest_path,
                    dry_run=True,
                    rollout_ids=["spectral", "spectral"],
                    runner=runner,
                )

        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            calls: list[str] = []

            def repeated_runner(root: Path, task_id: str, **kwargs) -> Path:
                calls.append(kwargs["rollout_strategy"]["rollout_id"])
                return self.dry_runner(root, task_id, **kwargs)

            ensemble = run_fanout(
                root,
                self.task_id,
                manifest_path,
                dry_run=True,
                rollout_ids=["spectral", "operator"],
                runner=repeated_runner,
            )
            value = read_json(ensemble)
            self.assertFalse(value["complete"])
            self.assertEqual(calls, ["spectral", "operator"])

    def test_full_non_dry_fanout_attests_each_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            ensemble = run_fanout(
                root,
                self.task_id,
                manifest_path,
                runner=self.completed_runner,
            )
            value = read_json(ensemble)
            self.assertTrue(value["complete"])
            self.assertFalse(value["dry_run"])
            self.assertTrue(
                all(record["status"] == "completed" for record in value["rollouts"])
            )
            self.assertTrue(
                all(len(record["run_attestation"]) == 9 for record in value["rollouts"])
            )

    def test_dynamic_verifier_artifact_is_bound_into_final_report_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            task_path = root / "research" / "tasks" / f"{self.task_id}.json"
            task = read_json(task_path)
            task["dynamic_verifier_artifacts"] = ["controls/dynamic.py"]
            task["required_artifacts"] = [
                *task["required_artifacts"],
                "controls/dynamic.py",
            ]
            write_json(task_path, task)
            ensemble = run_fanout(
                root,
                self.task_id,
                manifest_path,
                runner=self.completed_runner,
            )
            value = read_json(ensemble)
            self.assertTrue(all(record["status"] == "completed" for record in value["rollouts"]))
            self.assertIsNotNone(latest_completed_fanout(root, self.task_id))

    def test_cli_exposes_repeatable_rollout_and_merge_shards(self) -> None:
        parser = build_parser()
        fanout = parser.parse_args(
            [
                "fanout",
                self.task_id,
                "--manifest",
                "research/fanouts/fixture.json",
                "--rollout-id",
                "spectral",
                "--rollout-id",
                "operator",
            ]
        )
        self.assertEqual(fanout.rollout_ids, ["spectral", "operator"])
        merge = parser.parse_args(
            [
                "fanout-merge",
                self.task_id,
                "--manifest",
                "research/fanouts/fixture.json",
                "--shard",
                "runs/a/ensemble.json",
                "runs/b/ensemble.json",
            ]
        )
        self.assertEqual(len(merge.shard), 2)

    def test_sealed_fanout_cannot_override_statement_only_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary, sealed=True)
            manifest = self.manifest()
            manifest["rollouts"][1]["context_mode"] = "full_history"
            write_json(manifest_path, manifest)
            with self.assertRaisesRegex(ProtocolError, "context must match"):
                run_fanout(
                    root,
                    self.task_id,
                    manifest_path,
                    dry_run=True,
                    runner=self.dry_runner,
                )

    def test_manifest_must_be_repository_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external:
            root, _ = self.make_root(temporary)
            outside = Path(external) / "manifest.json"
            write_json(outside, self.manifest())
            with self.assertRaisesRegex(ProtocolError, "inside the repository"):
                run_fanout(
                    root,
                    self.task_id,
                    outside,
                    dry_run=True,
                    runner=self.dry_runner,
                )

    def test_task_declared_manifest_rejects_alternate_run_merge_and_consumer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, official = self.make_root(temporary)
            alternate = root / "research" / "fanouts" / "alternate.json"
            write_json(alternate, self.manifest())
            with self.assertRaisesRegex(ProtocolError, "task-declared official"):
                run_fanout(
                    root,
                    self.task_id,
                    alternate,
                    dry_run=True,
                    runner=self.dry_runner,
                )

            spectral, operator = self.make_shards(root, official)
            with self.assertRaisesRegex(ProtocolError, "task-declared official"):
                merge_fanout_shards(
                    root, self.task_id, alternate, [spectral, operator]
                )

            merged = merge_fanout_shards(
                root, self.task_id, official, [spectral, operator]
            )
            forged = read_json(merged)
            forged["source_manifest"] = alternate.relative_to(root).as_posix()
            forged["source_manifest_sha256"] = sha256_file(alternate)
            write_json(merged, forged)
            self.assertIsNone(latest_completed_fanout(root, self.task_id))

    def test_merge_validates_all_runs_and_preserves_complete_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            shards = self.make_shards(root, manifest_path)
            merged = merge_fanout_shards(
                root,
                self.task_id,
                manifest_path.relative_to(root),
                [path.relative_to(root) for path in shards],
            )
            value = read_json(merged)
            self.assertTrue(value["complete"])
            self.assertFalse(value["dry_run"])
            self.assertEqual(value["selected_rollout_ids"], ["spectral", "operator"])
            self.assertEqual(
                [record["rollout_id"] for record in value["rollouts"]],
                ["spectral", "operator"],
            )
            self.assertEqual(len(value["source_shards"]), 2)
            self.assertTrue(
                all(
                    not Path(entry["path"]).is_absolute() and len(entry["sha256"]) == 64
                    for entry in value["source_shards"]
                )
            )
            expected_attestation = {
                "invocation_sha256",
                "task_sha256",
                "validation_sha256",
                "result_sha256",
                "artifact_manifest_sha256",
                "trusted_preflight_sha256",
                "trusted_final_sha256",
                "artifact_tree_sha256",
                "verifier_log_tree_sha256",
            }
            self.assertTrue(
                all(
                    set(record["run_attestation"]) == expected_attestation
                    for record in value["rollouts"]
                )
            )
            completed = latest_completed_fanout(root, self.task_id)
            self.assertIsNotNone(completed)
            assert completed is not None
            self.assertEqual(completed[0], merged.parent)
            self.assertEqual(len(completed[1]), 2)

    def test_shards_from_two_account_roots_merge_after_transport(self) -> None:
        with (
            tempfile.TemporaryDirectory() as first_directory,
            tempfile.TemporaryDirectory() as second_directory,
            tempfile.TemporaryDirectory() as coordinator_directory,
        ):
            first, first_manifest = self.make_root(first_directory)
            second, second_manifest = self.make_root(second_directory)
            coordinator, coordinator_manifest = self.make_root(coordinator_directory)
            first_shard = run_fanout(
                first,
                self.task_id,
                first_manifest,
                rollout_ids=["spectral"],
                runner=self.completed_runner,
            )
            second_shard = run_fanout(
                second,
                self.task_id,
                second_manifest,
                rollout_ids=["operator"],
                runner=self.completed_runner,
            )

            transported: list[Path] = []
            for source_root, shard in (
                (first, first_shard),
                (second, second_shard),
            ):
                shard_value = read_json(shard)
                run_source = source_root / shard_value["rollouts"][0]["run_dir"]
                run_destination = coordinator / shard_value["rollouts"][0]["run_dir"]
                shutil.copytree(run_source, run_destination)
                shard_destination = coordinator / shard.relative_to(source_root)
                shutil.copytree(shard.parent, shard_destination.parent)
                transported.append(shard_destination)

            merged = merge_fanout_shards(
                coordinator,
                self.task_id,
                coordinator_manifest,
                transported,
            )
            self.assertTrue(read_json(merged)["complete"])
            self.assertIsNotNone(latest_completed_fanout(coordinator, self.task_id))

    def test_complete_consumer_rechecks_source_shard_lineage(self) -> None:
        for tamper in ("source_shard_file", "merged_source_pointer"):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as temporary:
                root, manifest_path = self.make_root(temporary)
                spectral, operator = self.make_shards(root, manifest_path)
                merged = merge_fanout_shards(
                    root, self.task_id, manifest_path, [spectral, operator]
                )
                if tamper == "source_shard_file":
                    value = read_json(spectral)
                    value["post_merge_tamper"] = True
                    write_json(spectral, value)
                else:
                    value = read_json(merged)
                    value["rollouts"][0]["source_shard_sha256"] = "0" * 64
                    write_json(merged, value)
                self.assertIsNone(latest_completed_fanout(root, self.task_id))

    def test_merge_rejects_duplicate_and_missing_rollouts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral = run_fanout(
                root,
                self.task_id,
                manifest_path,
                rollout_ids=["spectral"],
                runner=self.completed_runner,
            )
            with self.assertRaisesRegex(ProtocolError, "shard paths.*duplicates"):
                merge_fanout_shards(
                    root, self.task_id, manifest_path, [spectral, spectral]
                )
            with self.assertRaisesRegex(ProtocolError, "do not cover"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral])

            duplicate_dir = spectral.parent.parent / "ensemble-duplicate-rollout"
            duplicate_dir.mkdir()
            duplicate = read_json(spectral)
            duplicate["ensemble_id"] = duplicate_dir.name
            duplicate_path = duplicate_dir / "ensemble.json"
            write_json(duplicate_path, duplicate)
            with self.assertRaisesRegex(ProtocolError, "duplicate rollout_id"):
                merge_fanout_shards(
                    root, self.task_id, manifest_path, [spectral, duplicate_path]
                )

    def test_merge_rejects_wrong_manifest_hash_and_failed_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral, operator = self.make_shards(root, manifest_path)
            value = read_json(spectral)
            value["source_manifest_sha256"] = "0" * 64
            write_json(spectral, value)
            with self.assertRaisesRegex(ProtocolError, "source manifest lineage mismatch"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral, operator])

        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral, operator = self.make_shards(root, manifest_path)
            value = read_json(spectral)
            value["rollouts"][0]["status"] = "failed"
            write_json(spectral, value)
            with self.assertRaisesRegex(ProtocolError, "not completed"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral, operator])

        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral, operator = self.make_shards(root, manifest_path)
            value = read_json(spectral)
            value["task_id"] = "T999-wrong-task"
            write_json(spectral, value)
            with self.assertRaisesRegex(ProtocolError, "task or ensemble identity"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral, operator])

    def test_merge_rejects_dry_or_tampered_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            dry = run_fanout(
                root,
                self.task_id,
                manifest_path,
                dry_run=True,
                rollout_ids=["spectral"],
                runner=self.dry_runner,
            )
            with self.assertRaisesRegex(ProtocolError, "must be non-dry"):
                merge_fanout_shards(root, self.task_id, manifest_path, [dry])

        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral, operator = self.make_shards(root, manifest_path)
            shard = read_json(spectral)
            result_path = root / shard["rollouts"][0]["run_dir"] / "result.json"
            result = read_json(result_path)
            result["tampered_after_shard"] = True
            write_json(result_path, result)
            with self.assertRaisesRegex(ProtocolError, "SHA-256 mismatch"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral, operator])

        with tempfile.TemporaryDirectory() as temporary:
            root, manifest_path = self.make_root(temporary)
            spectral, operator = self.make_shards(root, manifest_path)
            shard = read_json(spectral)
            validation_path = root / shard["rollouts"][0]["run_dir"] / "validation.json"
            write_json(validation_path, {"valid": False, "errors": ["hostile failure"]})
            with self.assertRaisesRegex(ProtocolError, "invalid validation"):
                merge_fanout_shards(root, self.task_id, manifest_path, [spectral, operator])

    def test_merge_rejects_tampered_task_artifact_and_verifier_evidence(self) -> None:
        for tamper in (
            "self_attested_task_snapshot",
            "self_attested_forged_phase_time",
            "repository_source_input",
            "artifact_bytes",
            "missing_result_artifact",
            "self_attested_verifier_report",
            "verifier_log_bytes",
            "missing_preflight_report",
        ):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as temporary:
                root, manifest_path = self.make_root(temporary)
                if tamper == "repository_source_input":
                    source = root / "source.md"
                    source.write_text("source version one\n", encoding="utf-8")
                    task_path = root / "research" / "tasks" / f"{self.task_id}.json"
                    task = read_json(task_path)
                    task["inputs"] = ["source.md"]
                    write_json(task_path, task)
                spectral, operator = self.make_shards(root, manifest_path)
                shard = read_json(spectral)
                record = shard["rollouts"][0]
                run_dir = root / record["run_dir"]
                if tamper == "self_attested_task_snapshot":
                    target = run_dir / "task.json"
                    value = read_json(target)
                    value["objective"] = "attacker substituted another task"
                    write_json(target, value)
                    record["run_attestation"]["task_sha256"] = sha256_file(target)
                    write_json(spectral, shard)
                elif tamper == "self_attested_forged_phase_time":
                    target = run_dir / "invocation.json"
                    value = read_json(target)
                    value["phases"][0]["active_seconds"] = 1.0
                    write_json(target, value)
                    record["run_attestation"]["invocation_sha256"] = sha256_file(target)
                    write_json(spectral, shard)
                elif tamper == "repository_source_input":
                    (root / "source.md").write_text(
                        "source version two\n", encoding="utf-8"
                    )
                elif tamper == "artifact_bytes":
                    (run_dir / "artifacts" / "notes.md").write_text(
                        "changed after shard\n", encoding="utf-8"
                    )
                elif tamper == "missing_result_artifact":
                    hidden = run_dir / "artifacts" / "hidden.md"
                    target = run_dir / "result.json"
                    value = read_json(target)
                    value["artifacts"].append(
                        {"path": hidden.relative_to(root).as_posix()}
                    )
                    write_json(target, value)
                    record["run_attestation"]["result_sha256"] = sha256_file(target)
                    write_json(spectral, shard)
                elif tamper == "self_attested_verifier_report":
                    target = run_dir / "trusted_verifiers.json"
                    value = read_json(target)
                    value["records"][0]["command"] = ["python", "wrong_control.py"]
                    write_json(target, value)
                    record["run_attestation"]["trusted_final_sha256"] = sha256_file(target)
                    write_json(spectral, shard)
                elif tamper == "verifier_log_bytes":
                    target = next((run_dir / "verifiers").glob("*final*.stdout.log"))
                    target.write_text("forged log\n", encoding="utf-8")
                else:
                    (run_dir / "trusted_verifiers.preflight.json").unlink()

                with self.assertRaises(ProtocolError):
                    merge_fanout_shards(
                        root,
                        self.task_id,
                        manifest_path,
                        [spectral, operator],
                    )


if __name__ == "__main__":
    unittest.main()
