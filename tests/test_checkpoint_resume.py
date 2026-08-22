from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rpcd_harness.cli import build_parser
from rpcd_harness.codex_adapter import run_codex_task
from rpcd_harness.protocol import (
    ProtocolError,
    checkpoint_run,
    load_resume_checkpoint,
    read_json,
    repository_source_snapshot,
    sha256_file,
    write_json,
)


def resume_task() -> dict:
    return {
        "schema_version": "1.0",
        "task_id": "T900-resume-test",
        "title": "sealed checkpoint resume fixture",
        "role": "explorer",
        "objective": "deepen a locked RPCD route",
        "claim_ids": ["C050"],
        "dependencies": [],
        "inputs": ["statement.md"],
        "allowed_max_evidence": "E3",
        "required_artifacts": ["proof.md"],
        "acceptance_checks": ["preserve the locked route"],
        "route_ids": ["R140-direct-covariance-multiepoch"],
        "research_mode": "sealed_breadth",
        "context_policy": {
            "mode": "statement_only",
            "allowlist": ["statement.md"],
            "reveal_after_route_card": True,
        },
        "method_constraints": {
            "method_family": "direct-covariance-multiepoch",
            "forbidden_methods": [],
            "required_controls": ["fresh epoch permutations"],
        },
        "rollout_strategy": {
            "route_card_minutes": 20,
            "immutable_route_card": True,
        },
        "strict_claim_scope": True,
        "verifiers": [
            {
                "name": "portable exact smoke check",
                "command": ["{python}", "-c", "print('verified')"],
                "mode": "exact",
                "timeout_seconds": 10,
                "expected_exit_code": 0,
            }
        ],
        "status": "ready",
    }


def route_card() -> dict:
    return {
        "schema_version": "1.0",
        "route_card_id": "RC-resume-test",
        "task_id": "T900-resume-test",
        "rollout_id": "rollout-operator",
        "method_family": "direct-covariance-multiepoch",
        "representation": "the full covariance superoperator",
        "state_or_invariant": "the reachable PSD covariance cone",
        "core_candidate_lemma": "a two-epoch reachable-cone contraction",
        "predicted_failure": "non-normal transients destroy a uniform prefactor",
        "falsifier": "exact n=3 rational permutation enumeration",
        "target_implication": "the lemma implies the C050 expected-distance rate",
        "information_retained": ["full covariance orientation"],
        "information_discarded": ["pathwise order"],
        "context_mode": "statement_only",
        "parent_route_ids": ["R140-direct-covariance-multiepoch"],
    }


def phase_result(run_id: str, worker: str) -> dict:
    return {
        "schema_version": "1.0",
        "task_id": "T900-resume-test",
        "run_id": run_id,
        "worker": worker,
        "status": "partial",
        "summary": "the locked route remains open",
        "claims": [],
        "artifacts": [],
        "checks": [],
        "failed_attempts": [],
        "iteration": {
            "avenues": [
                {
                    "name": "operator route",
                    "objective": "test a covariance-power lemma",
                    "outcome": "open",
                    "status": "open",
                    "method_family": "direct-covariance-multiepoch",
                    "representation": "the full covariance superoperator",
                    "state_or_invariant": "the reachable PSD covariance cone",
                    "core_candidate_lemma": "a two-epoch reachable-cone contraction",
                    "information_retained": ["full covariance orientation"],
                    "information_discarded": ["pathwise order"],
                    "target_implication": "the lemma implies C050",
                    "predicted_failure": "non-normal transients",
                    "falsifier": "exact rational n=3 enumeration",
                    "context_mode": "statement_only",
                    "parent_route_ids": ["R140-direct-covariance-multiepoch"],
                }
            ],
            "checkpoints": [],
            "stress_tests": ["near singular", "noncommuting"],
            "deepest_obstruction": "the contraction constant is still open",
        },
        "literature": [],
        "next_tasks": [],
        "limitations": [],
    }


def build_incomplete_checkpoint(root: Path, *, locked_card: bool = True) -> tuple[Path, Path]:
    task = resume_task()
    (root / "prompts").mkdir(parents=True)
    (root / "prompts" / "common.md").write_text("COMMON", encoding="utf-8")
    (root / "prompts" / "explorer.md").write_text("ROLE", encoding="utf-8")
    (root / "research" / "tasks").mkdir(parents=True)
    (root / "research" / "routes").mkdir()
    write_json(
        root / "research" / "routes" / "R140-direct-covariance-multiepoch.json",
        {"route_id": "R140-direct-covariance-multiepoch"},
    )
    (root / "statement.md").write_text("RPCD STATEMENT", encoding="utf-8")
    write_json(root / "research" / "tasks" / f"{task['task_id']}.json", task)

    run_id = "20260823T000000Z-source"
    worker = "account-a"
    run_dir = root / "runs" / task["task_id"] / run_id
    artifacts = run_dir / "artifacts"
    events = run_dir / "events"
    artifacts.mkdir(parents=True)
    events.mkdir()
    (artifacts / "proof.md").write_text("inherited partial proof", encoding="utf-8")
    write_json(run_dir / "task.json", task)
    (run_dir / "phase-001-prompt.md").write_text("sealed phase", encoding="utf-8")
    (events / "phase-001.jsonl").write_text("{}\n", encoding="utf-8")
    (events / "phase-001.stderr.log").write_text("", encoding="utf-8")
    write_json(run_dir / "phase-001-result.json", phase_result(run_id, worker))
    write_json(
        run_dir / "phase-001-validation.json",
        {"valid": True, "minimum_active_time_reached": False, "errors": []},
    )
    strategy = {
        "rollout_id": "rollout-operator",
        "worker": worker,
        "method_family": "direct-covariance-multiepoch",
        "context_mode": "statement_only",
        "route_ids": ["R140-direct-covariance-multiepoch"],
    }
    invocation = {
        "schema_version": "1.0",
        "task_id": task["task_id"],
        "run_id": run_id,
        "worker": worker,
        "dry_run": False,
        "iteration_complete": False,
        "active_research_seconds": 60.0,
        "phases": [
            {
                "phase": 1,
                "active_seconds": 60.0,
                "cumulative_active_seconds": 60.0,
                "exit_code": 0,
                "prompt": (run_dir / "phase-001-prompt.md").relative_to(root).as_posix(),
                "result": (run_dir / "phase-001-result.json").relative_to(root).as_posix(),
                "events": (events / "phase-001.jsonl").relative_to(root).as_posix(),
                "stderr": (events / "phase-001.stderr.log").relative_to(root).as_posix(),
                "phase_kind": "sealed_route_card",
            }
        ],
        "research_mode": "sealed_breadth",
        "context_policy": task["context_policy"],
        "rollout_strategy": strategy,
        "repository_source_snapshot": repository_source_snapshot(root, task),
    }
    if locked_card:
        card_path = artifacts / "route_card.json"
        write_json(card_path, route_card())
        card_hash = sha256_file(card_path)
        invocation["route_card"] = {
            "path": card_path.relative_to(root).as_posix(),
            "sha256": card_hash,
            "staged_context": "external_ephemeral",
        }
        invocation["route_card_sha256"] = card_hash
    write_json(run_dir / "invocation.json", invocation)
    return run_dir, checkpoint_run(root, task["task_id"], run_dir)


class CheckpointResumeTests(unittest.TestCase):
    def test_cli_accepts_resume_checkpoint_path(self) -> None:
        args = build_parser().parse_args(
            [
                "run-codex",
                "T900-resume-test",
                "--worker",
                "account-b",
                "--resume-from-checkpoint",
                "research/checkpoints/source.json",
            ]
        )
        self.assertEqual(args.resume_from_checkpoint, Path("research/checkpoints/source.json"))

    def test_resume_loader_rejects_tamper_completed_and_unlocked_sealed_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            run_dir, checkpoint = build_incomplete_checkpoint(root)
            (run_dir / "artifacts" / "proof.md").write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ProtocolError, "byte count changed|SHA-256 mismatch"):
                load_resume_checkpoint(root, "T900-resume-test", checkpoint)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            run_dir, _ = build_incomplete_checkpoint(root)
            invocation = read_json(run_dir / "invocation.json")
            invocation["iteration_complete"] = True
            write_json(run_dir / "invocation.json", invocation)
            checkpoint = checkpoint_run(root, "T900-resume-test", run_dir)
            with self.assertRaisesRegex(ProtocolError, "completed runs cannot be resumed"):
                load_resume_checkpoint(root, "T900-resume-test", checkpoint)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _, checkpoint = build_incomplete_checkpoint(root, locked_card=False)
            with self.assertRaisesRegex(ProtocolError, "route card has been locked"):
                load_resume_checkpoint(root, "T900-resume-test", checkpoint)

    def test_resume_loader_rejects_source_drift_and_checkpoint_metadata_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _, checkpoint = build_incomplete_checkpoint(root)
            (root / "prompts" / "common.md").write_text("DRIFT", encoding="utf-8")
            with self.assertRaisesRegex(ProtocolError, "repository snapshot"):
                load_resume_checkpoint(root, "T900-resume-test", checkpoint)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _, checkpoint = build_incomplete_checkpoint(root)
            value = read_json(checkpoint)
            value["source_invocation_sha256"] = "0" * 64
            write_json(checkpoint, value)
            with self.assertRaisesRegex(ProtocolError, "source_invocation_sha256"):
                load_resume_checkpoint(root, "T900-resume-test", checkpoint)

    def test_dry_resume_copies_state_but_resets_credit_and_breadth_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source_run, checkpoint = build_incomplete_checkpoint(root)
            new_run = run_codex_task(
                root,
                "T900-resume-test",
                "account-b",
                dry_run=True,
                resume_from_checkpoint=checkpoint,
            )

            self.assertNotEqual(new_run, source_run)
            invocation = read_json(new_run / "invocation.json")
            self.assertEqual(invocation["research_mode"], "continuation_depth")
            self.assertEqual(invocation["context_policy"]["mode"], "full_history")
            self.assertIsNone(invocation["rollout_strategy"])
            self.assertEqual(invocation["active_research_seconds"], 0.0)
            self.assertFalse(invocation["iteration_complete"])
            self.assertFalse(invocation["eligible_for_fanout"])
            lineage = invocation["resume_lineage"]
            self.assertFalse(lineage["independence"])
            self.assertFalse(lineage["eligible_for_fanout"])
            self.assertFalse(lineage["counts_as_new_breadth"])
            self.assertEqual(lineage["credited_active_research_seconds"], 0.0)
            self.assertEqual(lineage["source_active_research_seconds"], 60.0)
            self.assertEqual(len(lineage["checkpoint_sha256"]), 64)
            self.assertEqual(
                (new_run / "artifacts" / "proof.md").read_text(encoding="utf-8"),
                "inherited partial proof",
            )
            self.assertEqual(
                sha256_file(new_run / "artifacts" / "route_card.json"),
                invocation["route_card_sha256"],
            )
            self.assertFalse((new_run / "sealed-context.json").exists())
            prompt = (new_run / "prompt.md").read_text(encoding="utf-8")
            self.assertIn("Checkpoint continuation (not independent breadth)", prompt)
            self.assertIn("independence=false", prompt)
            self.assertIn("starts at `0.00` credited active minutes", prompt)
            self.assertIn("# Locked route card", prompt)
            self.assertNotIn("# Sealed route-card phase", prompt)

    def test_resume_rejects_attempt_to_supply_a_new_rollout_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _, checkpoint = build_incomplete_checkpoint(root)
            with self.assertRaisesRegex(ProtocolError, "cannot be launched as a new independent"):
                run_codex_task(
                    root,
                    "T900-resume-test",
                    "account-b",
                    dry_run=True,
                    resume_from_checkpoint=checkpoint,
                    rollout_strategy={"rollout_id": "new"},
                )

    def test_executed_resume_earns_a_fresh_full_floor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _, checkpoint = build_incomplete_checkpoint(root)
            monotonic_values = iter([100.0, 7300.0])

            def fake_codex(command: list[str], **kwargs: object) -> SimpleNamespace:
                phase_path = Path(command[-2])
                result = phase_result(phase_path.parent.name, "account-b")
                proof = phase_path.parent / "artifacts" / "proof.md"
                result["artifacts"] = [
                    {
                        "path": proof.relative_to(root).as_posix(),
                        "kind": "proof",
                        "description": "inherited and deepened proof draft",
                    }
                ]
                result["iteration"]["checkpoints"] = [
                    {
                        "elapsed_active_minutes": 30 * index,
                        "summary": f"checkpoint {index}",
                        "next_action": "continue",
                    }
                    for index in range(1, 5)
                ]
                self.assertEqual(Path(kwargs["cwd"]).resolve(), root)
                self.assertIn("independence=false", str(kwargs["input"]))
                write_json(phase_path, result)
                return SimpleNamespace(returncode=0)

            with patch(
                "rpcd_harness.codex_adapter.subprocess.run", side_effect=fake_codex
            ), patch(
                "rpcd_harness.codex_adapter.time.monotonic",
                side_effect=lambda: next(monotonic_values),
            ), patch(
                "rpcd_harness.codex_adapter.run_verifiers", return_value=([], [])
            ):
                new_run = run_codex_task(
                    root,
                    "T900-resume-test",
                    "account-b",
                    resume_from_checkpoint=checkpoint,
                )

            invocation = read_json(new_run / "invocation.json")
            self.assertTrue(invocation["iteration_complete"])
            self.assertEqual(invocation["active_research_seconds"], 7200.0)
            self.assertEqual(len(invocation["phases"]), 1)
            self.assertEqual(invocation["phases"][0]["phase_kind"], "research")
            self.assertEqual(
                invocation["resume_lineage"]["credited_active_research_seconds"], 0.0
            )


if __name__ == "__main__":
    unittest.main()
