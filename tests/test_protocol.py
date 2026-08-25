from __future__ import annotations

import hashlib
import unittest
import tempfile
from pathlib import Path

from rpcd_harness.protocol import (
    ProtocolError,
    audit_claim_ledger,
    dependency_result_paths,
    find_root,
    latest_completed_fanout,
    list_tasks,
    load_iteration_policy,
    load_task,
    read_json,
    repository_source_snapshot,
    unmet_task_dependencies,
    sha256_file,
    validate_result,
    validate_task,
    write_json,
)


def base_result() -> dict:
    return {
        "schema_version": "1.0",
        "task_id": "T010-matrix-jensen",
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
                {"name": "a", "objective": "a", "outcome": "a", "status": "blocked"},
                {"name": "b", "objective": "b", "outcome": "b", "status": "blocked"},
                {"name": "c", "objective": "c", "outcome": "c", "status": "blocked"},
            ],
            "checkpoints": [],
            "stress_tests": ["stress one", "stress two"],
            "deepest_obstruction": "test obstruction",
        },
        "literature": [],
        "next_tasks": [],
        "limitations": [],
    }


def dependency_task(task_id: str, *, status: str = "ready") -> dict:
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "title": "dependency fixture",
        "role": "researcher",
        "objective": "produce dependency evidence",
        "claim_ids": [],
        "dependencies": [],
        "inputs": ["statement.md"],
        "allowed_max_evidence": "E2",
        "required_artifacts": [],
        "acceptance_checks": [],
        "status": status,
    }


def completed_run(
    root: Path,
    task_id: str,
    run_id: str,
    *,
    iteration_complete: bool = True,
    valid: bool = True,
    include_result: bool = True,
) -> Path:
    run_dir = root / "runs" / task_id / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "artifacts").mkdir()
    task_path = root / "research" / "tasks" / f"{task_id}.json"
    task_value = read_json(task_path) if task_path.is_file() else dependency_task(task_id)
    write_json(run_dir / "task.json", task_value)
    preflight_path = run_dir / "trusted_verifiers.preflight.json"
    write_json(
        preflight_path,
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
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
            "task_id": task_id,
            "run_id": run_id,
            "records": [],
            "errors": [],
        },
    )
    write_json(
        run_dir / "invocation.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "iteration_complete": iteration_complete,
            "active_research_seconds": 7200.0,
            "phases": [
                {"phase": 1, "active_seconds": 7200.0, "exit_code": 0}
            ],
            "repository_source_snapshot": repository_source_snapshot(root, task_value),
            "cwd": str(root.resolve()),
            "preflight_verifiers": {
                "path": preflight_path.relative_to(root).as_posix(),
                "status": "not_configured",
                "valid": True,
            },
        },
    )
    write_json(run_dir / "validation.json", {"valid": valid, "errors": []})
    if include_result:
        write_json(
            run_dir / "result.json",
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "artifacts": [],
            },
        )
    write_json(
        run_dir / "artifact_manifest.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "files": [],
        },
    )
    return run_dir


def ensemble_record(root: Path, run_dir: Path, rollout_id: str) -> dict:
    worker = f"worker-{rollout_id}"
    family = f"family-{rollout_id}"
    strategy = {
        "rollout_id": rollout_id,
        "worker": worker,
        "method_family": family,
        "context_mode": "statement_only",
        "route_ids": [],
        "objective": f"objective-{rollout_id}",
        "forbidden_methods": [],
        "required_controls": [f"control-{rollout_id}"],
    }
    invocation_path = run_dir / "invocation.json"
    invocation = read_json(invocation_path)
    invocation.update(
        task_id=run_dir.parent.name,
        run_id=run_dir.name,
        worker=worker,
        dry_run=False,
        exit_code=0,
        rollout_strategy=strategy,
    )
    write_json(invocation_path, invocation)
    validation_path = run_dir / "validation.json"
    validation = read_json(validation_path)
    validation.setdefault("errors", [])
    write_json(validation_path, validation)
    result_path = run_dir / "result.json"
    if result_path.is_file():
        result = read_json(result_path)
        result.update(task_id=run_dir.parent.name, run_id=run_dir.name, worker=worker)
        write_json(result_path, result)

    def digest_or_missing(path: Path) -> str:
        # Malformed-run fixtures still need an ensemble record so the
        # consumer, rather than this fixture helper, rejects the missing file.
        return sha256_file(path) if path.is_file() else "0" * 64

    return {
        "rollout_id": rollout_id,
        "worker": worker,
        "method_family": family,
        "status": "completed",
        "run_dir": run_dir.relative_to(root).as_posix(),
        "run_attestation": {
            "invocation_sha256": digest_or_missing(run_dir / "invocation.json"),
            "task_sha256": digest_or_missing(run_dir / "task.json"),
            "validation_sha256": digest_or_missing(run_dir / "validation.json"),
            "result_sha256": digest_or_missing(run_dir / "result.json"),
            "artifact_manifest_sha256": digest_or_missing(
                run_dir / "artifact_manifest.json"
            ),
            "trusted_preflight_sha256": digest_or_missing(
                run_dir / "trusted_verifiers.preflight.json"
            ),
            "trusted_final_sha256": digest_or_missing(
                run_dir / "trusted_verifiers.json"
            ),
            "artifact_tree_sha256": hashlib.sha256(b"{}").hexdigest(),
            "verifier_log_tree_sha256": hashlib.sha256(b"{}").hexdigest(),
        },
    }


def write_ensemble(
    root: Path,
    task_id: str,
    ensemble_id: str,
    rollouts: list[dict],
    *,
    dry_run: bool = False,
    complete: bool = True,
) -> Path:
    source_manifest = root / "research" / "fanouts" / f"{ensemble_id}.json"
    source_rollouts = [
        {
            "rollout_id": rollout["rollout_id"],
            "worker": rollout["worker"],
            "method_family": rollout["method_family"],
            "context_mode": "statement_only",
            "route_ids": [],
            "objective": f"objective-{rollout['rollout_id']}",
            "forbidden_methods": [],
            "required_controls": [f"control-{rollout['rollout_id']}"],
        }
        for rollout in rollouts
    ]
    write_json(
        source_manifest,
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "rollouts": source_rollouts,
        },
    )
    path = root / "runs" / task_id / "ensembles" / ensemble_id / "ensemble.json"
    write_json(
        path,
        {
            "schema_version": "1.0",
            "kind": "rpcd-independent-rollout-ensemble",
            "ensemble_id": ensemble_id,
            "task_id": task_id,
            "dry_run": dry_run,
            "complete": complete,
            "source_manifest": source_manifest.relative_to(root).as_posix(),
            "source_manifest_sha256": sha256_file(source_manifest),
            "selected_rollout_ids": [
                rollout["rollout_id"] for rollout in source_rollouts
            ],
            "distinct_method_families": sorted(
                {rollout["method_family"] for rollout in source_rollouts}
            ),
            "rollouts": rollouts,
        },
    )
    return path


class ProtocolTests(unittest.TestCase):
    def test_dependency_mode_validation_and_default(self) -> None:
        task = dependency_task("T901-dependency")
        validate_task(task)
        for mode in ("latest_validated_run", "complete_validated_fanout"):
            with self.subTest(mode=mode):
                validate_task({**task, "dependency_mode": mode})
        with self.assertRaisesRegex(ProtocolError, "invalid dependency_mode"):
            validate_task({**task, "dependency_mode": "any-successful-rollout"})
        with self.assertRaisesRegex(ProtocolError, "invalid dependency_mode"):
            validate_task({**task, "dependency_mode": ["latest_validated_run"]})

    def test_complete_fanout_dependency_returns_every_result_from_latest_ensemble(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tasks = root / "research" / "tasks"
            tasks.mkdir(parents=True)
            (root / "statement.md").write_text("statement", encoding="utf-8")
            task_id = "T901-dependency"
            write_json(tasks / f"{task_id}.json", dependency_task(task_id))
            dependent = {
                "dependencies": [task_id],
                "dependency_mode": "complete_validated_fanout",
            }

            old_runs = [
                completed_run(root, task_id, "20260822T000000Z-old-a"),
                completed_run(root, task_id, "20260822T000001Z-old-b"),
            ]
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T000002Z-old",
                [
                    ensemble_record(root, old_runs[0], "old-a"),
                    ensemble_record(root, old_runs[1], "old-b"),
                ],
            )
            latest_runs = [
                completed_run(root, task_id, "20260822T000003Z-latest-a"),
                completed_run(root, task_id, "20260822T000004Z-latest-b"),
                completed_run(root, task_id, "20260822T000005Z-latest-c"),
            ]
            latest_ensemble = write_ensemble(
                root,
                task_id,
                "ensemble-20260822T000006Z-latest",
                [
                    ensemble_record(root, latest_runs[0], "latest-a"),
                    ensemble_record(root, latest_runs[1], "latest-b"),
                    ensemble_record(root, latest_runs[2], "latest-c"),
                ],
            )
            # A newer partial ensemble must not shadow the newest complete one.
            partial_run = completed_run(root, task_id, "20260821T235957Z-partial")
            partial = [ensemble_record(root, partial_run, "partial")]
            partial[0]["status"] = "prepared"
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T000007Z-partial",
                partial,
                complete=False,
            )
            # A shard may contain only successful runs (even every selected
            # ID) but it is not canonical until fanout-merge attests the full
            # manifest with complete=true.
            shard_runs = [
                completed_run(root, task_id, "20260821T235958Z-shard-a"),
                completed_run(root, task_id, "20260821T235959Z-shard-b"),
            ]
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T000009Z-successful-shard",
                [
                    ensemble_record(root, shard_runs[0], "shard-a"),
                    ensemble_record(root, shard_runs[1], "shard-b"),
                ],
                complete=False,
            )

            selected = latest_completed_fanout(root, task_id)
            self.assertIsNotNone(selected)
            assert selected is not None
            self.assertEqual(selected[0], latest_ensemble.parent)
            expected = [
                (run_dir / "result.json").relative_to(root).as_posix()
                for run_dir in latest_runs
            ]
            self.assertEqual(dependency_result_paths(root, dependent), expected)
            self.assertEqual(unmet_task_dependencies(root, dependent), [])
            # Omitting dependency_mode preserves the historical one-run
            # selection even when that run also belongs to an ensemble.
            self.assertEqual(
                dependency_result_paths(root, {"dependencies": [task_id]}),
                [expected[-1]],
            )

    def test_partial_or_failed_fanout_cannot_be_replaced_by_one_valid_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tasks = root / "research" / "tasks"
            tasks.mkdir(parents=True)
            (root / "statement.md").write_text("statement", encoding="utf-8")
            task_id = "T901-dependency"
            # Even a task-level done flag cannot waive the downstream request
            # for a complete fanout dependency.
            write_json(tasks / f"{task_id}.json", dependency_task(task_id, status="done"))
            dependent = {
                "dependencies": [task_id],
                "dependency_mode": "complete_validated_fanout",
            }
            run_a = completed_run(root, task_id, "20260822T010000Z-a")
            run_b = completed_run(root, task_id, "20260822T010001Z-b")
            partial_records = [
                ensemble_record(root, run_a, "a"),
                ensemble_record(root, run_b, "b"),
            ]
            partial_records[1]["status"] = "prepared"
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T010002Z-partial",
                partial_records,
            )
            failed_records = [
                ensemble_record(root, run_a, "a-failed"),
                ensemble_record(root, run_b, "b-failed"),
            ]
            failed_records[0]["status"] = "failed"
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T010003Z-failed",
                failed_records,
            )
            write_ensemble(
                root,
                task_id,
                "ensemble-20260822T010004Z-dry",
                [
                    ensemble_record(root, run_a, "a-dry"),
                    ensemble_record(root, run_b, "b-dry"),
                ],
                dry_run=True,
            )

            self.assertIsNone(latest_completed_fanout(root, task_id))
            self.assertEqual(dependency_result_paths(root, dependent), [])
            self.assertEqual(unmet_task_dependencies(root, dependent), [task_id])

    def test_tampered_ensemble_paths_and_run_attestations_are_rejected(self) -> None:
        tamper_cases = (
            "path_escape",
            "incomplete",
            "invalid",
            "missing_result",
            "deleted_rollout",
            "forged_invocation",
            "short_runtime",
            "forged_result",
            "validation_errors",
        )
        for tamper in tamper_cases:
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                tasks = root / "research" / "tasks"
                tasks.mkdir(parents=True)
                (root / "statement.md").write_text("statement", encoding="utf-8")
                task_id = "T901-dependency"
                write_json(tasks / f"{task_id}.json", dependency_task(task_id))
                dependent = {
                    "dependencies": [task_id],
                    "dependency_mode": "complete_validated_fanout",
                }
                run_a = completed_run(root, task_id, "20260822T020000Z-a")
                run_b = completed_run(
                    root,
                    task_id,
                    "20260822T020001Z-b",
                    iteration_complete=tamper != "incomplete",
                    valid=tamper != "invalid",
                    include_result=tamper != "missing_result",
                )
                records = [
                    ensemble_record(root, run_a, "a"),
                    ensemble_record(root, run_b, "b"),
                ]
                if tamper == "path_escape":
                    outside = completed_run(root, "T999-other", "escaped")
                    records[1]["run_dir"] = outside.relative_to(root).as_posix()
                ensemble_path = write_ensemble(
                    root,
                    task_id,
                    "ensemble-20260822T020002Z-tampered",
                    records,
                )
                if tamper == "deleted_rollout":
                    tampered = read_json(ensemble_path)
                    tampered["rollouts"].pop()
                    write_json(ensemble_path, tampered)
                elif tamper in {
                    "forged_invocation",
                    "short_runtime",
                    "forged_result",
                    "validation_errors",
                }:
                    tampered = read_json(ensemble_path)
                    if tamper in {"forged_invocation", "short_runtime"}:
                        target = run_b / "invocation.json"
                        value = read_json(target)
                        if tamper == "forged_invocation":
                            value.update(task_id="T999-wrong", dry_run=True, exit_code=99)
                        else:
                            value["active_research_seconds"] = 0.0
                    elif tamper == "forged_result":
                        target = run_b / "result.json"
                        value = read_json(target)
                        value.update(task_id="T999-wrong", worker="wrong-worker")
                    else:
                        target = run_b / "validation.json"
                        value = {"valid": True, "errors": ["not actually clean"]}
                    write_json(target, value)
                    key = {
                        "invocation.json": "invocation_sha256",
                        "result.json": "result_sha256",
                        "validation.json": "validation_sha256",
                    }[target.name]
                    tampered["rollouts"][1]["run_attestation"][key] = sha256_file(target)
                    write_json(ensemble_path, tampered)

                self.assertIsNone(latest_completed_fanout(root, task_id))
                self.assertEqual(dependency_result_paths(root, dependent), [])
                self.assertEqual(unmet_task_dependencies(root, dependent), [task_id])

    def test_iteration_policy_has_two_hour_floor(self) -> None:
        policy = load_iteration_policy(find_root())
        self.assertGreaterEqual(policy["minimum_active_minutes_per_worker"], 120)

    def test_iteration_floor_is_checked_against_harness_time(self) -> None:
        result = base_result()
        errors = validate_result(
            result,
            iteration_policy=load_iteration_policy(find_root()),
            active_seconds=119 * 60,
        )
        self.assertTrue(any("below the iteration floor" in error for error in errors))

    def test_result_semantic_checks_preserve_transport_schema_constraints(self) -> None:
        result = base_result()
        result["iteration"]["avenues"][0]["name"] = "   "
        result["iteration"]["avenues"][0]["parent_route_ids"] = ["R100", "R100"]
        result["iteration"]["checkpoints"] = [
            {
                "elapsed_active_minutes": -1,
                "summary": "",
                "next_action": "   ",
            }
        ]
        errors = validate_result(result)
        self.assertTrue(any("name must be a non-empty string" in error for error in errors))
        self.assertTrue(any("must not contain duplicates" in error for error in errors))
        self.assertTrue(any("non-negative number" in error for error in errors))
        self.assertTrue(any("summary must be a non-empty string" in error for error in errors))
        self.assertTrue(any("next_action must be a non-empty string" in error for error in errors))

    def test_null_continuation_parent_ids_returns_errors(self) -> None:
        task = dependency_task("T901-null-parent")
        task["research_mode"] = "continuation_depth"
        task["route_ids"] = ["R111-general-w4"]
        result = base_result()
        result["task_id"] = task["task_id"]
        result["iteration"]["avenues"] = [
            {
                "name": "null parent control",
                "objective": "exercise type handling",
                "outcome": "invalid parent list",
                "status": "blocked",
                "parent_route_ids": None,
                "source_layer": "L2",
                "next_layer": "L3",
                "branch_kind": "depth",
            }
        ]
        errors = validate_result(result, task=task)
        self.assertTrue(any("parent_route_ids must be an array" in error for error in errors))
        self.assertTrue(any("not linked to an assigned route" in error for error in errors))

    def test_all_tasks_are_well_formed(self) -> None:
        root = find_root()
        tasks = list_tasks(root)
        self.assertGreaterEqual(len(tasks), 8)

    def test_ledger_is_consistent(self) -> None:
        self.assertEqual(audit_claim_ledger(find_root()), [])

    def test_theorem_gate_evidence_separates_proof_and_priority_workers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            claims = root / "research" / "claims"
            claims.mkdir(parents=True)
            artifact = root / "proof.md"
            artifact.write_text("proof", encoding="utf-8")
            claim = {
                "schema_version": "1.0",
                "claim_id": "C999",
                "status": "theorem_candidate",
                "evidence_level": "E5",
                "supporting_artifacts": ["proof.md"],
                "gates": {
                    "finite_statement": True,
                    "quantifiers_explicit": True,
                    "domain_expert_spec_review": True,
                    "proof_draft": True,
                    "hostile_audit": True,
                    "independent_reconstruction": True,
                    "priority_audit": True,
                },
            }
            write_json(claims / "C999-test.json", claim)
            errors = audit_claim_ledger(root)
            self.assertTrue(any("gate_evidence" in error for error in errors))

            claim["gate_evidence"] = {
                gate: {
                    "worker": "same-worker",
                    "run_id": f"run-{gate}",
                    "artifacts": ["proof.md"],
                }
                for gate in (
                    "finite_statement",
                    "quantifiers_explicit",
                    "domain_expert_spec_review",
                    "proof_draft",
                    "hostile_audit",
                    "independent_reconstruction",
                    "priority_audit",
                )
            }
            write_json(claims / "C999-test.json", claim)
            errors = audit_claim_ledger(root)
            self.assertTrue(any("distinct workers" in error for error in errors))

    def test_theorem_candidate_requires_independent_reconstruction_level(self) -> None:
        result = base_result()
        result["claims"] = [
            {
                "claim_id": "C010",
                "statement": "candidate",
                "status": "theorem_candidate",
                "evidence_level": "E4",
                "assumptions": [],
                "supporting_artifacts": [],
                "open_objections": [],
            }
        ]
        errors = validate_result(result)
        self.assertTrue(any("requires E5" in error for error in errors))

    def test_self_reported_failed_check_and_unauthorized_master_refutation_fail(self) -> None:
        task = dependency_task("T901-critic-contract")
        task["research_mode"] = "critic_validation"
        task["strict_claim_scope"] = True
        task["claim_ids"] = ["C050"]
        result = base_result()
        result["task_id"] = task["task_id"]
        result["checks"] = [
            {"command": "python control.py", "exit_code": 3, "summary": "failed"}
        ]
        result["claims"] = [
            {
                "claim_id": "C050",
                "statement": "a route lemma failed",
                "status": "refuted",
                "evidence_level": "E2",
                "assumptions": [],
                "supporting_artifacts": [],
                "open_objections": [],
            }
        ]
        errors = validate_result(result, task=task)
        self.assertTrue(any("did not pass" in error for error in errors))
        self.assertTrue(any("not authorized" in error for error in errors))

    def test_strict_claim_binding_rejects_route_lemma_mislabeled_as_c050(self) -> None:
        root = find_root()
        task = load_task(root, "T143-sealed-finite-time-breadth")
        result = base_result()
        result["task_id"] = task["task_id"]
        result["claims"] = [
            {
                "claim_id": "C050",
                "statement": "A local covariance lemma",
                "statement_ref": "research/problem.md#current-finite-time-target",
                "status": "idea",
                "evidence_level": "E1",
                "assumptions": [],
                "supporting_artifacts": [],
                "open_objections": [],
            }
        ]
        errors = validate_result(result, task=task, root=root)
        self.assertTrue(any("canonical claim title" in error for error in errors))

        result["claims"][0]["statement"] = "General finite-time expected-distance RPCD complexity"
        result["claims"][0]["statement_ref"] = "wrong-section"
        errors = validate_result(result, task=task, root=root)
        self.assertTrue(any("statement_ref" in error for error in errors))

    def test_artifact_path_cannot_escape_repo(self) -> None:
        result = base_result()
        result["artifacts"] = [
            {"path": "../secret", "kind": "data", "description": "bad"}
        ]
        errors = validate_result(result)
        self.assertTrue(any("unsafe relative path" in error for error in errors))

    def test_windows_drive_and_unc_inputs_are_not_repository_relative(self) -> None:
        for hostile in (
            r"C:\Windows\win.ini",
            r"\\server\share\statement.md",
            ".",
            "statement.md\x00hidden",
            "statement.md:alternate-stream",
            "NUL.txt",
            "trailing. ",
        ):
            with self.subTest(hostile=hostile):
                task = dependency_task("T901-drive-escape")
                task["inputs"] = [hostile]
                with self.assertRaisesRegex(ProtocolError, "unsafe input path"):
                    validate_task(task)

    def test_fanout_manifest_and_optional_control_fields_are_typed(self) -> None:
        task = dependency_task("T901-manifest-fields")
        validate_task(
            {
                **task,
                "fanout_manifest": "research/fanouts/official.json",
                "may_refute_master_claim": False,
                "strict_claim_binding": True,
                "required_artifacts": [*task["required_artifacts"], "exact_control.py"],
                "dynamic_verifier_artifacts": ["exact_control.py"],
            }
        )
        for hostile in (
            r"C:\outside.json",
            r"\\server\share\manifest.json",
            "research/other/manifest.json",
            r"research\fanouts\manifest.json",
        ):
            with self.subTest(hostile=hostile), self.assertRaises(ProtocolError):
                validate_task({**task, "fanout_manifest": hostile})
        for field in (
            "may_refute_master_claim",
            "strict_claim_binding",
            "require_distinct_dependency_workers",
        ):
            with self.subTest(field=field), self.assertRaisesRegex(
                ProtocolError, "must be a boolean"
            ):
                validate_task({**task, field: "false"})

    def test_t143_is_bound_to_the_repository_owned_official_manifest(self) -> None:
        task = load_task(find_root(), "T143-sealed-finite-time-breadth")
        self.assertEqual(
            task.get("fanout_manifest"),
            "research/fanouts/T143-initial-breadth.json",
        )
        snapshot = repository_source_snapshot(find_root(), task)
        paths = {entry["path"] for entry in snapshot["files"]}
        for required in (
            "research/problem.md",
            "prompts/common.md",
            "prompts/explorer.md",
            "research/iteration_policy.json",
            "research/portfolio_policy.json",
            "pyproject.toml",
            "constraints.txt",
            "scripts/verify_rpcd_identities.py",
            "scripts/iter6_projection_lift.py",
            "research/fanouts/T143-initial-breadth.json",
            "rpcd_harness/protocol.py",
            "schemas/result.schema.json",
            "schemas/result.structured.schema.json",
        ):
            with self.subTest(required=required):
                self.assertIn(required, paths)
        self.assertEqual(len(snapshot["tree_sha256"]), 64)

    def test_depth_mode_allows_one_real_route_instead_of_three_cosmetic_avenues(self) -> None:
        root = find_root()
        task = load_task(root, "T140-general-w4-overlap")
        result = base_result()
        result["task_id"] = task["task_id"]
        result["iteration"]["avenues"] = [
            {
                "name": "general W4 repair",
                "objective": "close the first anisotropic Schur edge",
                "outcome": "one exact edge remains open",
                "status": "advanced",
                "route_id": "R112-stable-bellman-depth",
                "parent_route_ids": ["R111-general-w4"],
                "source_layer": "L2",
                "next_layer": "L3",
                "branch_kind": "depth",
                "first_bad_edge": "aggregate child recovery does not yet close W4",
                "core_candidate_lemma": "directional W4 recovery",
                "predicted_failure": "an unequal star destroys scalar recovery",
                "falsifier": "exact unequal-star principal minors",
                "decision": "deepen",
            }
        ]
        errors = validate_result(result, task=task)
        self.assertFalse(any("too few distinct avenues" in error for error in errors))
        self.assertFalse(any("not linked to an assigned route" in error for error in errors))

    def test_depth_task_must_select_one_frontier_and_one_adjacent_child_edge(self) -> None:
        root = find_root()
        task = load_task(root, "T140-general-w4-overlap")
        with self.assertRaisesRegex(ProtocolError, "exactly one active frontier"):
            validate_task({**task, "route_ids": ["R110-bellman-schur", "R111-general-w4"]})

        result = base_result()
        result["task_id"] = task["task_id"]
        result["iteration"]["avenues"] = [
            {
                "name": "invalid layer skip",
                "objective": "skip the first bad edge",
                "outcome": "invalid",
                "status": "advanced",
                "route_id": "R199-invalid-skip",
                "parent_route_ids": ["R111-general-w4"],
                "source_layer": "L2",
                "next_layer": "L4",
                "branch_kind": "depth",
                "first_bad_edge": "unproved W4 aggregation",
                "core_candidate_lemma": "skip directly to a terminal certificate",
                "predicted_failure": "the missing L3 edge remains unproved",
                "falsifier": "inspect the parent implication",
                "decision": "deepen",
            }
        ]
        errors = validate_result(result, task=task)
        self.assertTrue(any("immediately below source_layer" in error for error in errors))

    def test_depth_bottleneck_requires_repair_and_attack_children(self) -> None:
        task = load_task(find_root(), "T140-general-w4-overlap")
        result = base_result()
        result["task_id"] = task["task_id"]
        child = {
            "name": "repair child",
            "objective": "retain the anisotropic surplus",
            "outcome": "blocked at the aggregate edge",
            "status": "blocked",
            "route_id": "R198-repair-child",
            "parent_route_ids": ["R111-general-w4"],
            "source_layer": "L2",
            "next_layer": "L3",
            "branch_kind": "repair",
            "first_bad_edge": "aggregate recovery loses the child direction",
            "core_candidate_lemma": "a matrix-valued repair state",
            "predicted_failure": "a frustrated cycle defeats the repair",
            "falsifier": "exact frustrated-cycle Schur calculation",
            "decision": "branch",
        }
        result["iteration"]["avenues"] = [child]
        errors = validate_result(result, task=task)
        self.assertTrue(any("repair and attack" in error for error in errors))

        attack = dict(child)
        attack.update(
            {
                "name": "attack child",
                "route_id": "R197-attack-child",
                "branch_kind": "attack",
                "core_candidate_lemma": "the W4 edge fails on a P4 block",
            }
        )
        result["iteration"]["avenues"] = [child, attack]
        errors = validate_result(result, task=task)
        self.assertFalse(any("repair and attack" in error for error in errors))

    def test_critic_mode_requires_two_distinct_attacks(self) -> None:
        task = load_task(find_root(), "T144-audit-sealed-finite-time-route")
        result = base_result()
        result["task_id"] = task["task_id"]
        result["iteration"]["avenues"] = [
            {
                "name": "orientation attack",
                "objective": "reconstruct transpose order",
                "outcome": "open",
                "status": "open",
                "representation": "covariance superoperator",
                "first_bad_edge": "one-step covariance identity to finite-time contraction",
                "predicted_failure": "product orientation is reversed",
                "falsifier": "exact n=3 enumeration",
                "decision": "deepen",
            }
        ]
        errors = validate_result(result, task=task)
        self.assertTrue(any("too few distinct avenues" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
