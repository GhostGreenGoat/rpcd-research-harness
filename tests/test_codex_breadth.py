from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rpcd_harness.codex_adapter import render_prompt, run_codex_task
from rpcd_harness.protocol import (
    DEFAULT_ITERATION_POLICY,
    ProtocolError,
    find_root,
    load_task,
    latest_completed_run,
    read_json,
    repository_source_snapshot,
    unmet_task_dependencies,
    validate_result,
    validate_route_card,
    validate_task,
    write_json,
)


def minimal_task(task_id: str = "T900-sealed-test") -> dict:
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "title": "Sealed direct covariance test",
        "role": "explorer",
        "objective": "Find a direct covariance route to the finite-time RPCD target.",
        "claim_ids": ["C050"],
        "dependencies": [],
        "inputs": ["statement.md", "history/old-proof.md"],
        "allowed_max_evidence": "E3",
        "required_artifacts": ["proof.md"],
        "acceptance_checks": ["HISTORY-CHECK-MUST-NOT-LEAK-IN-PHASE-ONE"],
        "route_ids": ["R140-direct-covariance-multiepoch"],
        "research_mode": "sealed_breadth",
        "context_policy": {
            "mode": "statement_only",
            "allowlist": ["statement.md"],
            "denylist": ["history/old-proof.md"],
            "reveal_after_route_card": True,
        },
        "method_constraints": {
            "method_family": "direct-covariance-multiepoch",
            "forbidden_methods": ["fixed-A terminal certificate"],
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


def valid_route_card() -> dict:
    return {
        "schema_version": "1.0",
        "route_card_id": "RC-direct-covariance",
        "task_id": "T900-sealed-test",
        "rollout_id": "rollout-operator",
        "method_family": "direct-covariance-multiepoch",
        "representation": "the full covariance superoperator",
        "state_or_invariant": "the reachable PSD covariance cone",
        "core_candidate_lemma": "a two-epoch reachable-cone contraction",
        "predicted_failure": "non-normal transients destroy a uniform prefactor",
        "falsifier": "exact n=3 permutation enumeration over a rational family",
        "target_implication": "the lemma implies the C050 expected-distance rate",
        "information_retained": ["full covariance orientation"],
        "information_discarded": ["pathwise order"],
        "context_mode": "statement_only",
        "parent_route_ids": ["R140-direct-covariance-multiepoch"],
    }


def base_result(task_id: str = "T900-sealed-test") -> dict:
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": "run-test",
        "worker": "tester",
        "status": "partial",
        "summary": "test",
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
                    "representation": "full covariance operator",
                    "state_or_invariant": "reachable PSD cone",
                    "core_candidate_lemma": "two-epoch cone contraction",
                    "information_retained": ["full covariance orientation"],
                    "information_discarded": ["pathwise order"],
                    "target_implication": "the lemma implies C050",
                    "predicted_failure": "non-normal prefactor",
                    "falsifier": "exact rational n=3 enumeration",
                    "context_mode": "statement_only",
                    "parent_route_ids": ["R140-direct-covariance-multiepoch"],
                }
            ],
            "checkpoints": [],
            "stress_tests": ["near singular", "noncommuting"],
            "deepest_obstruction": "test obstruction",
        },
        "literature": [],
        "next_tasks": [],
        "limitations": [],
    }


class CodexBreadthProtocolTests(unittest.TestCase):
    def test_route_card_checks_lineage_family_context_and_content(self) -> None:
        task = minimal_task()
        strategy = {
            "rollout_id": "rollout-operator",
            "method_family": "direct-covariance-multiepoch",
            "context_mode": "statement_only",
        }
        self.assertEqual(
            validate_route_card(valid_route_card(), task=task, rollout_strategy=strategy),
            [],
        )

        bad = valid_route_card()
        bad["rollout_id"] = "another-rollout"
        bad["method_family"] = "fixed-energy"
        bad["context_mode"] = "full_history"
        bad["falsifier"] = ""
        errors = validate_route_card(bad, task=task, rollout_strategy=strategy)
        self.assertTrue(any("rollout_id" in error for error in errors))
        self.assertTrue(any("method_family" in error for error in errors))
        self.assertTrue(any("context_mode" in error for error in errors))
        self.assertTrue(any("falsifier" in error for error in errors))

    def test_route_card_rejects_undeclared_fields_and_duplicate_parents(self) -> None:
        task = minimal_task()
        strategy = {
            "rollout_id": "rollout-operator",
            "method_family": "direct-covariance-multiepoch",
            "context_mode": "statement_only",
        }
        card = valid_route_card()
        card["private_history_summary"] = "must never enter a sealed card"
        card["parent_route_ids"] *= 2
        errors = validate_route_card(card, task=task, rollout_strategy=strategy)
        self.assertTrue(any("unsupported" in error for error in errors))
        self.assertTrue(any("parent_route_ids" in error for error in errors))

    def test_route_card_parent_lineage_must_match_assigned_route_nodes(self) -> None:
        task = minimal_task()
        strategy = {
            "rollout_id": "rollout-operator",
            "method_family": "direct-covariance-multiepoch",
            "context_mode": "statement_only",
            "route_ids": ["R100-l0-finite-time"],
        }
        card = valid_route_card()
        errors = validate_route_card(card, task=task, rollout_strategy=strategy)
        self.assertTrue(any("parent" in error and "assigned" in error for error in errors))

    def test_sealed_prompt_omits_denied_history_and_full_acceptance_contract(self) -> None:
        task = minimal_task()
        task["objective"] += " HISTORY-OBJECTIVE-MUST-WAIT-UNTIL-REVEAL"
        task["method_constraints"]["forbidden_methods"].append(
            "HISTORY-METHOD-BARRIER-MUST-WAIT-UNTIL-REVEAL"
        )
        task["verifiers"][0]["command"] = [
            "{python}",
            "history/HISTORY-VERIFIER-MUST-WAIT-UNTIL-REVEAL.py",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "prompts").mkdir()
            (root / "prompts" / "common.md").write_text("COMMON", encoding="utf-8")
            (root / "prompts" / "explorer.md").write_text("ROLE", encoding="utf-8")
            output = root / "runs" / "task" / "run" / "artifacts"
            output.mkdir(parents=True)
            prompt = render_prompt(
                root,
                task,
                "run-test",
                "worker",
                output,
                DEFAULT_ITERATION_POLICY,
                rollout_strategy={
                    "rollout_id": "rollout-operator",
                    "method_family": "direct-covariance-multiepoch",
                    "context_mode": "statement_only",
                    "objective": "HISTORY-STRATEGY-OBJECTIVE-MUST-WAIT-UNTIL-REVEAL",
                    "forbidden_methods": ["HISTORY-STRATEGY-BARRIER"],
                    "required_controls": ["HISTORY-STRATEGY-CONTROL"],
                },
                route_card_only=True,
            )
        self.assertIn("statement.md", prompt)
        self.assertNotIn("history/old-proof.md", prompt)
        self.assertNotIn("HISTORY-CHECK-MUST-NOT-LEAK-IN-PHASE-ONE", prompt)
        self.assertNotIn("HISTORY-VERIFIER-MUST-WAIT-UNTIL-REVEAL", prompt)
        self.assertNotIn("HISTORY-OBJECTIVE-MUST-WAIT-UNTIL-REVEAL", prompt)
        self.assertNotIn("HISTORY-METHOD-BARRIER-MUST-WAIT-UNTIL-REVEAL", prompt)
        self.assertNotIn("HISTORY-STRATEGY-OBJECTIVE-MUST-WAIT-UNTIL-REVEAL", prompt)
        self.assertNotIn("HISTORY-STRATEGY-BARRIER", prompt)
        self.assertNotIn("HISTORY-STRATEGY-CONTROL", prompt)
        self.assertNotIn("proof.md", prompt)
        self.assertIn("route_card.json", prompt)

    def test_rollout_strategy_cannot_inject_unvalidated_history_metadata(self) -> None:
        task = minimal_task()
        sentinel = "PRIVATE-HISTORY-SUMMARY-SENTINEL"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "prompts").mkdir()
            (root / "prompts" / "common.md").write_text("COMMON", encoding="utf-8")
            (root / "prompts" / "explorer.md").write_text("ROLE", encoding="utf-8")
            output = root / "runs" / "task" / "run" / "artifacts"
            output.mkdir(parents=True)
            prompt = render_prompt(
                root,
                task,
                "run-test",
                "worker",
                output,
                DEFAULT_ITERATION_POLICY,
                rollout_strategy={
                    "rollout_id": "rollout-operator",
                    "method_family": "direct-covariance-multiepoch",
                    "context_mode": "statement_only",
                    "private_notes": sentinel,
                },
                route_card_only=True,
            )
        self.assertNotIn(sentinel, prompt)

    def test_t143_shared_contract_does_not_force_one_of_its_four_method_families(self) -> None:
        root = find_root()
        t143_tasks = list((root / "research" / "tasks").glob("T143-*.json"))
        self.assertEqual(len(t143_tasks), 1)
        task = load_task(root, t143_tasks[0].stem)
        contract = "\n".join(
            [
                *task["required_artifacts"],
                *task["acceptance_checks"],
                *task.get("method_constraints", {}).get("required_differences", []),
            ]
        ).lower()
        for direct_only_fragment in (
            "immutable_route_card.json",
            "direct_covariance_representation.md",
            "multiepoch_candidate.md",
            "primary state is the full second-moment covariance",
            "core lemma genuinely operator- or multi-epoch-valued",
        ):
            self.assertNotIn(direct_only_fragment.lower(), contract)

    def test_sealed_result_uses_rollout_family_not_base_task_placeholder(self) -> None:
        task = minimal_task()
        task["method_constraints"]["method_family"] = "base-placeholder-family"
        strategy = {
            "rollout_id": "rollout-operator",
            "worker": "tester",
            "method_family": "assigned-exchangeable-family",
            "context_mode": "statement_only",
            "route_ids": ["R140-direct-covariance-multiepoch"],
        }
        result = base_result()
        result["iteration"]["avenues"][0]["method_family"] = strategy["method_family"]
        errors = validate_result(result, task=task, rollout_strategy=strategy)
        self.assertFalse(any("assigned method_family" in error for error in errors))
        base_errors = validate_result(result, task=task)
        self.assertTrue(any("assigned method_family" in error for error in base_errors))

    def test_required_artifact_declarations_are_enforced(self) -> None:
        task = minimal_task()
        result = base_result()
        result["artifacts"] = [
            {
                "path": "runs/T900/run/artifacts/proof.md",
                "kind": "proof",
                "description": "proof",
            }
        ]
        task["required_artifacts"] = ["proof.md", "falsifier.py"]
        errors = validate_result(result, task=task)
        self.assertFalse(any("proof.md" in error for error in errors))
        self.assertTrue(any("falsifier.py" in error for error in errors))

    def test_task_rejects_unsafe_or_malformed_verifier_before_launch(self) -> None:
        task = minimal_task()
        task["verifiers"] = [
            {
                "name": "unsafe late failure",
                "command": ["powershell", "-Command", "Write-Output unsafe"],
                "mode": "symbolic",
                "timeout_seconds": False,
                "expected_exit_code": 0,
            }
        ]
        with self.assertRaisesRegex(ProtocolError, "verifier"):
            validate_task(task)

    def test_duplicate_structured_avenue_signature_is_rejected(self) -> None:
        result = base_result()
        duplicate = copy.deepcopy(result["iteration"]["avenues"][0])
        duplicate["name"] = "renamed but mathematically identical"
        duplicate["objective"] = "rephrased objective"
        duplicate["outcome"] = "different prose"
        result["iteration"]["avenues"].append(duplicate)
        errors = validate_result(result, task=minimal_task())
        self.assertTrue(any("duplicate mathematical signatures" in error for error in errors))

    def test_unmet_dependency_detects_blocked_and_missing_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tasks = root / "research" / "tasks"
            tasks.mkdir(parents=True)
            (root / "statement.md").write_text("statement", encoding="utf-8")
            dependency = minimal_task("T901-dependency")
            dependency["research_mode"] = "critic_validation"
            dependency["context_policy"] = {"mode": "declared_inputs"}
            dependency["inputs"] = ["statement.md"]
            dependency["route_ids"] = []
            dependency["status"] = "blocked"
            dependency["dependencies"] = []
            write_json(tasks / "T901-dependency.json", dependency)
            task = minimal_task("T902-dependent")
            task["dependencies"] = ["T901-dependency", "T999-missing"]
            self.assertEqual(
                unmet_task_dependencies(root, task),
                ["T901-dependency", "T999-missing"],
            )
            dependency["status"] = "done"
            write_json(tasks / "T901-dependency.json", dependency)
            self.assertEqual(
                unmet_task_dependencies(root, task),
                ["T901-dependency", "T999-missing"],
            )

    def test_validated_run_satisfies_dependency_without_mutating_task_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tasks = root / "research" / "tasks"
            tasks.mkdir(parents=True)
            (root / "statement.md").write_text("statement", encoding="utf-8")
            dependency = minimal_task("T901-dependency")
            dependency["research_mode"] = "critic_validation"
            dependency["context_policy"] = {"mode": "declared_inputs"}
            dependency["inputs"] = ["statement.md"]
            dependency["route_ids"] = []
            dependency["verifiers"] = []
            dependency["required_artifacts"] = []
            dependency["status"] = "ready"
            write_json(tasks / "T901-dependency.json", dependency)
            task = minimal_task("T902-dependent")
            task["dependencies"] = ["T901-dependency"]
            self.assertEqual(unmet_task_dependencies(root, task), ["T901-dependency"])

            run_dir = root / "runs" / "T901-dependency" / "20260822T000000Z-test"
            run_dir.mkdir(parents=True)
            (run_dir / "artifacts").mkdir()
            write_json(run_dir / "task.json", dependency)
            preflight = run_dir / "trusted_verifiers.preflight.json"
            write_json(
                preflight,
                {
                    "schema_version": "1.0",
                    "task_id": "T901-dependency",
                    "run_id": run_dir.name,
                    "phase": "preflight",
                    "status": "not_configured",
                    "records": [],
                    "errors": [],
                },
            )
            write_json(
                run_dir / "trusted_verifiers.json",
                {
                    "schema_version": "1.0",
                    "task_id": "T901-dependency",
                    "run_id": run_dir.name,
                    "records": [],
                    "errors": [],
                },
            )
            write_json(
                run_dir / "invocation.json",
                {
                    "schema_version": "1.0",
                    "task_id": "T901-dependency",
                    "run_id": run_dir.name,
                    "worker": "dependency-worker",
                    "dry_run": False,
                    "iteration_complete": True,
                    "active_research_seconds": 7200.0,
                    "exit_code": 0,
                    "phases": [
                        {"phase": 1, "active_seconds": 7200.0, "exit_code": 0}
                    ],
                    "rollout_strategy": None,
                    "repository_source_snapshot": repository_source_snapshot(
                        root, dependency
                    ),
                    "cwd": str(root.resolve()),
                    "preflight_verifiers": {
                        "path": preflight.relative_to(root).as_posix(),
                        "status": "not_configured",
                        "valid": True,
                    },
                },
            )
            write_json(run_dir / "validation.json", {"valid": True, "errors": []})
            write_json(
                run_dir / "result.json",
                {
                    "schema_version": "1.0",
                    "task_id": "T901-dependency",
                    "run_id": run_dir.name,
                    "worker": "dependency-worker",
                    "artifacts": [],
                },
            )
            write_json(
                run_dir / "artifact_manifest.json",
                {
                    "schema_version": "1.0",
                    "task_id": "T901-dependency",
                    "run_id": run_dir.name,
                    "files": [],
                },
            )
            self.assertEqual(latest_completed_run(root, "T901-dependency"), run_dir)
            self.assertEqual(unmet_task_dependencies(root, task), [])

            weak = root / "runs" / "T901-dependency" / "20260822T000001Z-weak"
            weak.mkdir()
            write_json(weak / "invocation.json", {"iteration_complete": True})
            write_json(weak / "validation.json", {"valid": True})
            write_json(weak / "result.json", {"task_id": "T901-dependency"})
            self.assertEqual(latest_completed_run(root, "T901-dependency"), run_dir)

    def test_adapter_blocks_unmet_dependency_before_creating_a_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch("rpcd_harness.codex_adapter.load_task", return_value=minimal_task()), patch(
                "rpcd_harness.codex_adapter.unmet_task_dependencies",
                return_value=["T901-blocked"],
            ):
                with self.assertRaisesRegex(ProtocolError, "unmet dependencies"):
                    run_codex_task(root, "T900-sealed-test", "worker", dry_run=True)
            self.assertFalse((root / "runs").exists())

    def test_critic_cannot_override_dependencies_or_audit_its_own_rollout(self) -> None:
        task = minimal_task("T903-critic")
        task["research_mode"] = "critic_validation"
        task["context_policy"] = {"mode": "declared_inputs"}
        task["route_ids"] = []
        task.pop("rollout_strategy")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            with patch("rpcd_harness.codex_adapter.load_task", return_value=task), patch(
                "rpcd_harness.codex_adapter.unmet_task_dependencies",
                return_value=["T900-upstream"],
            ):
                with self.assertRaisesRegex(ProtocolError, "not admissible"):
                    run_codex_task(
                        root,
                        task["task_id"],
                        "same-worker",
                        dry_run=True,
                        allow_unmet_dependencies=True,
                    )

            dependency_run = root / "runs" / "T900-upstream" / "run-upstream"
            dependency_run.mkdir(parents=True)
            write_json(
                dependency_run / "invocation.json",
                {"worker": "same-worker", "iteration_complete": True},
            )
            write_json(dependency_run / "result.json", {"worker": "same-worker"})
            relative_result = (dependency_run / "result.json").relative_to(root).as_posix()
            with patch("rpcd_harness.codex_adapter.load_task", return_value=task), patch(
                "rpcd_harness.codex_adapter.unmet_task_dependencies", return_value=[]
            ), patch(
                "rpcd_harness.codex_adapter.dependency_result_paths",
                return_value=[relative_result],
            ):
                with self.assertRaisesRegex(ProtocolError, "must differ"):
                    run_codex_task(root, task["task_id"], "same-worker", dry_run=True)

            second_run = root / "runs" / "T901-other" / "run-other"
            second_run.mkdir(parents=True)
            write_json(
                second_run / "invocation.json",
                {"worker": "same-worker", "iteration_complete": True},
            )
            write_json(second_run / "result.json", {"worker": "same-worker"})
            second_relative = (second_run / "result.json").relative_to(root).as_posix()
            distinct_task = {**task, "require_distinct_dependency_workers": True}
            with patch(
                "rpcd_harness.codex_adapter.load_task", return_value=distinct_task
            ), patch(
                "rpcd_harness.codex_adapter.unmet_task_dependencies", return_value=[]
            ), patch(
                "rpcd_harness.codex_adapter.dependency_result_paths",
                return_value=[relative_result, second_relative],
            ):
                with self.assertRaisesRegex(ProtocolError, "mutually distinct"):
                    run_codex_task(root, task["task_id"], "new-worker", dry_run=True)


class SealedRunIntegrationTests(unittest.TestCase):
    def test_nonsealed_preflight_failure_stops_before_codex_research(self) -> None:
        task = minimal_task("T901-preflight-stop")
        task["research_mode"] = "critic_validation"
        task["context_policy"] = {"mode": "declared_inputs"}
        task["route_ids"] = []
        task.pop("rollout_strategy")
        task["verifiers"] = [
            {
                "name": "known false inherited edge",
                "command": ["{python}", "-c", "raise SystemExit(9)"],
                "mode": "exact",
                "timeout_seconds": 10,
                "expected_exit_code": 0,
                "when": "preflight",
            }
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "prompts").mkdir()
            (root / "prompts" / "common.md").write_text("COMMON", encoding="utf-8")
            (root / "prompts" / "explorer.md").write_text("ROLE", encoding="utf-8")
            (root / "research" / "tasks").mkdir(parents=True)
            (root / "statement.md").write_text("RPCD STATEMENT", encoding="utf-8")
            (root / "history").mkdir()
            (root / "history" / "old-proof.md").write_text("OLD", encoding="utf-8")
            write_json(root / "research" / "tasks" / f"{task['task_id']}.json", task)

            with self.assertRaisesRegex(ProtocolError, "trusted preflight failed"):
                run_codex_task(root, task["task_id"], "worker", codex="must-not-launch")

            run_dirs = [path for path in (root / "runs" / task["task_id"]).iterdir()]
            self.assertEqual(len(run_dirs), 1)
            invocation = read_json(run_dirs[0] / "invocation.json")
            self.assertTrue(invocation["preflight_failed"])
            self.assertFalse(invocation["iteration_complete"])
            self.assertNotIn("phases", invocation)
            report = read_json(run_dirs[0] / "trusted_verifiers.preflight.json")
            self.assertNotEqual(report["errors"], [])
            self.assertEqual(report["records"][0]["status"], "failed")

    def test_two_phase_sealed_run_locks_card_then_runs_trusted_verifier(self) -> None:
        task = minimal_task()
        task["route_ids"] = []
        task["verifiers"][0]["when"] = "both"
        strategy = {
            "rollout_id": "rollout-operator",
            "method_family": "direct-covariance-multiepoch",
            "context_mode": "statement_only",
            "route_ids": ["R140-direct-covariance-multiepoch"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "prompts").mkdir()
            (root / "prompts" / "common.md").write_text("COMMON", encoding="utf-8")
            (root / "prompts" / "explorer.md").write_text("ROLE", encoding="utf-8")
            (root / "schemas").mkdir()
            (root / "research" / "tasks").mkdir(parents=True)
            (root / "statement.md").write_text("RPCD STATEMENT", encoding="utf-8")
            (root / "history").mkdir()
            (root / "history" / "old-proof.md").write_text(
                "PRIVATE OLD PROOF", encoding="utf-8"
            )
            write_json(root / "research" / "tasks" / f"{task['task_id']}.json", task)
            calls = 0
            real_subprocess_run = subprocess.run
            real_monotonic = time.monotonic
            phase_times = iter([0.0, 1.0, 1.0, 7201.0])

            def fake_monotonic() -> float:
                try:
                    return next(phase_times)
                except StopIteration:
                    return real_monotonic()

            def fake_codex(command: list[str], **kwargs: object) -> SimpleNamespace:
                nonlocal calls
                if Path(command[0]).resolve() == Path(sys.executable).resolve():
                    return real_subprocess_run(command, **kwargs)
                calls += 1
                self.assertEqual(kwargs.get("encoding"), "utf-8")
                sandbox_index = command.index("--sandbox") + 1
                self.assertEqual(command[sandbox_index], "workspace-write")
                schema_index = command.index("--output-schema") + 1
                self.assertEqual(
                    Path(command[schema_index]).name,
                    "result.structured.schema.json",
                )
                phase_result = Path(command[-2])
                run_dir = phase_result.parent
                if calls == 1:
                    self.assertIn("--skip-git-repo-check", command)
                    self.assertNotIn("history/old-proof.md", str(kwargs["input"]))
                    self.assertNotIn("Trusted preflight", str(kwargs["input"]))
                    staged_cwd = Path(kwargs["cwd"]).resolve()
                    self.assertTrue(staged_cwd.name.startswith("rpcd-sealed-"))
                    with self.assertRaises(ValueError):
                        staged_cwd.relative_to(root)
                    self.assertTrue((staged_cwd / "statement.md").is_file())
                    self.assertFalse(
                        (staged_cwd / "history" / "old-proof.md").exists()
                    )
                    staged_metadata = read_json(staged_cwd / "sealed-context.json")
                    self.assertNotIn("denylist", staged_metadata)
                    self.assertNotIn("old-proof", str(staged_metadata))
                    write_json(Path(kwargs["cwd"]) / "route_card.json", valid_route_card())
                else:
                    self.assertNotIn("--skip-git-repo-check", command)
                    self.assertIn("Trusted preflight", str(kwargs["input"]))
                    proof = run_dir / "artifacts" / "proof.md"
                    proof.write_text("candidate proof", encoding="utf-8")
                result = base_result()
                result["run_id"] = run_dir.name
                result["worker"] = "worker"
                result["iteration"]["checkpoints"] = [
                    {
                        "elapsed_active_minutes": 30 * index,
                        "summary": f"checkpoint {index}",
                        "next_action": "continue",
                    }
                    for index in range(1, 5)
                ]
                if calls > 1:
                    proof = run_dir / "artifacts" / "proof.md"
                    result["artifacts"] = [
                        {
                            "path": proof.relative_to(root).as_posix(),
                            "kind": "proof",
                            "description": "candidate proof",
                        }
                    ]
                write_json(phase_result, result)
                return SimpleNamespace(returncode=0)

            def fake_verifiers(
                specs: list[dict], **kwargs: object
            ) -> tuple[list[dict], list[str]]:
                verifier_phase = str(kwargs.get("phase", "final"))
                return (
                    [
                        {
                            "name": specs[0]["name"],
                            "status": "passed",
                            "passed": True,
                            "phase": verifier_phase,
                            "when": specs[0]["when"],
                            "command": [sys.executable],
                            "errors": [],
                        }
                    ],
                    [],
                )

            with patch("rpcd_harness.codex_adapter.subprocess.run", side_effect=fake_codex), patch(
                "rpcd_harness.codex_adapter.time.monotonic",
                side_effect=fake_monotonic,
            ), patch(
                "rpcd_harness.codex_adapter.run_verifiers",
                side_effect=fake_verifiers,
            ):
                run_dir = run_codex_task(
                    root,
                    task["task_id"],
                    "worker",
                    rollout_strategy=strategy,
                )

            self.assertEqual(calls, 2)
            invocation = read_json(run_dir / "invocation.json")
            self.assertTrue(invocation["iteration_complete"])
            source_snapshot = invocation["repository_source_snapshot"]
            self.assertEqual(source_snapshot["algorithm"], "sha256")
            self.assertEqual(len(source_snapshot["tree_sha256"]), 64)
            self.assertIn(
                "statement.md",
                {entry["path"] for entry in source_snapshot["files"]},
            )
            self.assertEqual(
                [phase["phase_kind"] for phase in invocation["phases"]],
                ["sealed_route_card", "research"],
            )
            locked_card = run_dir / "artifacts" / "route_card.json"
            self.assertTrue(locked_card.is_file())
            self.assertEqual(invocation["route_card_sha256"], invocation["route_card"]["sha256"])
            self.assertEqual(invocation["route_card"]["staged_context"], "external_ephemeral")
            self.assertTrue((run_dir / "sealed-context.json").is_file())
            trusted = read_json(run_dir / "trusted_verifiers.json")
            self.assertEqual(trusted["errors"], [])
            self.assertEqual(trusted["records"][0]["status"], "passed")
            preflight = read_json(run_dir / "trusted_verifiers.preflight.json")
            self.assertEqual(preflight["errors"], [])
            self.assertEqual(preflight["records"][0]["status"], "passed")
            self.assertEqual(preflight["records"][0]["phase"], "preflight")
            self.assertEqual(trusted["records"][0]["phase"], "final")
            self.assertEqual(
                Path(trusted["records"][0]["command"][0]).resolve(),
                Path(sys.executable).resolve(),
            )
            manifest_paths = {
                entry["path"] for entry in read_json(run_dir / "artifact_manifest.json")["files"]
            }
            self.assertIn(locked_card.relative_to(root).as_posix(), manifest_paths)


if __name__ == "__main__":
    unittest.main()
