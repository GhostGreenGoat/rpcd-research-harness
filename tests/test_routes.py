from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from rpcd_harness.cli import build_parser
from rpcd_harness.protocol import repository_source_snapshot
from rpcd_harness.routes import (
    DEFAULT_PORTFOLIO_POLICY,
    audit_route_repository,
    audit_portfolio,
    active_frontier_routes,
    can_reopen,
    find_exact_signature_duplicates,
    import_route_card,
    import_continuation_result,
    load_portfolio_policy,
    load_route_nodes,
    plan_route_allocation,
    prune_route,
    recommend_route,
    is_sealed_breadth_route,
    review_route_target,
    validate_continuation_avenue,
    validate_route_node,
    validate_route_dag,
    RouteError,
)
from rpcd_harness.fanout import _validated_run_attestation, load_fanout_manifest


RUN_ATTESTATION_KEYS = {
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


def route_node(
    route_id: str,
    layer: str,
    parent_ids: list[str],
    *,
    family: str = "bellman-schur",
    search_mode: str = "inherited_depth",
) -> dict:
    node = {
        "schema_version": "1.0",
        "route_id": route_id,
        "layer": layer,
        "title": f"RPCD route {route_id}",
        "statement": "Advance the normalized RPCD finite-time expected-distance target.",
        "parent_ids": parent_ids,
        "method_family": family,
        "target_claim_id": "G-FT",
        "signature": {
            "representation": f"representation {route_id}",
            "state_or_invariant": f"state {route_id}",
            "core_candidate_lemma": f"lemma {route_id}",
            "information_retained": ["permutation dependence", "matrix anisotropy"],
            "information_discarded": ["pathwise coordinate history"],
            "target_implication": "A valid bound implies the finite-time expected A-distance rate.",
            "known_failure_mode": "A scalar row sum can lose aggregate anisotropic surplus.",
            "verifier_class": "exact rational permutation enumeration",
        },
        "status": "active",
        "decision": "deepen",
        "merge_target_id": None,
        "reopen_if": [],
        "score": {
            "target_transfer": 2,
            "counterexample_resistance": 2,
            "blocker_specificity": 2,
            "falsifiability": 2,
            "recent_information_gain": 1,
        },
        "provenance": {
            "search_mode": search_mode,
            "initial_context": "statement_only" if search_mode == "sealed_breadth" else "full_repository",
            "route_card_hash": "a" * 64 if search_mode == "sealed_breadth" else None,
        },
    }
    if search_mode == "sealed_breadth":
        node["provenance"].update(
            route_card_origin="agent_generated",
            agent_rollout_id=f"rollout-{route_id.lower()}",
            agent_worker=f"generator-{route_id.lower()}",
            agent_run_id=f"run-{route_id.lower()}",
            independent_breadth_eligible=True,
            resumed_from_checkpoint=False,
            source_card_path=f"research/routes/cards/{route_id}.json",
            source_review_path=f"research/routes/reviews/{route_id}.json",
            route_review_hash="b" * 64,
            reviewer_task_id=f"T999-review-{route_id.lower()}",
            reviewer_worker=f"reviewer-{route_id.lower()}",
            reviewer_run_id=f"review-run-{route_id.lower()}",
            reviewer_run_attestation={key: "c" * 64 for key in RUN_ATTESTATION_KEYS},
        )
    return node


def layered_routes() -> list[dict]:
    return [
        route_node("R100", "L0", [], family="finite-time-target"),
        route_node("R110", "L1", ["R100"], family="bellman-schur"),
        route_node("R120", "L2", ["R110"], family="adaptive-prefix-state"),
        route_node("R130", "L3", ["R120"], family="w4-overlap"),
        route_node("R140", "L4", ["R130"], family="exact-structure-tests"),
    ]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_empty_trusted_reports(root: Path, run_dir: Path, task_id: str) -> None:
    """Create canonical no-verifier reports for an atomic fixture rollout."""

    run_id = run_dir.name
    write_json(
        run_dir / "trusted_verifiers.preflight.json",
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


def write_artifact_manifest(root: Path, run_dir: Path, task_id: str) -> None:
    files = []
    artifact_dir = run_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for artifact in sorted(path for path in artifact_dir.rglob("*") if path.is_file()):
        files.append(
            {
                "path": artifact.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "bytes": artifact.stat().st_size,
            }
        )
    write_json(
        run_dir / "artifact_manifest.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_dir.name,
            "files": files,
        },
    )


def finalize_completed_reviewer_run(
    root: Path,
    *,
    task_id: str,
    run_id: str,
    worker: str,
    artifacts: list[Path],
) -> Path:
    """Create canonical completed-run evidence around reviewer artifacts."""

    run_dir = root / "runs" / task_id / run_id
    task = {
        "schema_version": "1.0",
        "task_id": task_id,
        "title": "independent route transition reviewer fixture",
        "role": "skeptic",
        "objective": "independently review one RPCD route transition",
        "claim_ids": [],
        "dependencies": [],
        "inputs": [],
        "allowed_max_evidence": "E2",
        "required_artifacts": [],
        "acceptance_checks": [],
        "verifiers": [],
        "status": "ready",
    }
    write_json(root / "research" / "tasks" / f"{task_id}.json", task)
    write_json(run_dir / "task.json", task)
    write_json(
        run_dir / "result.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "worker": worker,
            "artifacts": [
                {"path": artifact.relative_to(root).as_posix()} for artifact in artifacts
            ],
        },
    )
    write_json(run_dir / "validation.json", {"valid": True, "errors": []})
    write_empty_trusted_reports(root, run_dir, task_id)
    write_artifact_manifest(root, run_dir, task_id)
    write_json(
        run_dir / "invocation.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "worker": worker,
            "dry_run": False,
            "iteration_complete": True,
            "active_research_seconds": 7200.0,
            "exit_code": 0,
            "rollout_strategy": None,
            "repository_source_snapshot": repository_source_snapshot(root, task),
            "cwd": str(root.resolve()),
            "preflight_verifiers": {
                "path": (run_dir / "trusted_verifiers.preflight.json")
                .relative_to(root)
                .as_posix(),
                "status": "not_configured",
                "valid": True,
            },
            "phases": [
                {
                    "phase": 1,
                    "phase_kind": "research",
                    "active_seconds": 7200.0,
                    "exit_code": 0,
                }
            ],
        },
    )
    return run_dir


def sealed_import_fixture(root: Path, *, standalone: bool = False) -> dict[str, Path]:
    task_id = "T900-sealed-import"
    run_id = "run-agent-001"
    run_dir = root / "runs" / task_id / run_id
    card_path = run_dir / "artifacts" / "route_card.json"
    parent_id = "R100-l0-target"
    parent = route_node(parent_id, "L0", [], family="finite-time-target")
    write_json(root / "research" / "routes" / f"{parent_id}.json", parent)

    strategy = {
        "rollout_id": "coupling-rollout",
        "worker": "sealed-worker-coupling",
        "method_family": "exchangeable-pair-permutation-coupling",
        "context_mode": "statement_only",
        "route_ids": [parent_id],
        "objective": "Derive an RPCD contraction from an exchangeable permutation pair.",
        "forbidden_methods": ["copying a coordinator route"],
        "required_controls": ["an exact adjacent-transposition identity"],
    }
    second_strategy = {
        "rollout_id": "operator-rollout",
        "worker": "sealed-worker-operator",
        "method_family": "covariance-superoperator-block-powers",
        "context_mode": "statement_only",
        "route_ids": [parent_id],
        "objective": "Derive an RPCD contraction from covariance block powers.",
        "forbidden_methods": ["copying the coupling route"],
        "required_controls": ["one exact non-normal block-power identity"],
    }
    manifest_path = root / "research" / "fanouts" / "T900-sealed-import.json"
    manifest = {
        "schema_version": "1.0",
        "task_id": task_id,
        "rollouts": [strategy, second_strategy],
    }
    card = {
        "schema_version": "1.0",
        "route_card_id": "card-coupling-rollout",
        "task_id": task_id,
        "rollout_id": strategy["rollout_id"],
        "method_family": strategy["method_family"],
        "representation": "Exchangeable random permutations differing by one adjacent transposition.",
        "state_or_invariant": "Conditional variance of the A-energy decrement under the coupled pair.",
        "core_candidate_lemma": "The coupled decrement controls mu times the current A-energy without a factor n.",
        "predicted_failure": "The transposition variance proxy may lose one factor n on anisotropic cycles.",
        "falsifier": "Exact rational enumeration on a four-coordinate frustrated cycle.",
        "target_implication": "A dimension-free conditional decrement iterates to the C050 expected-distance rate.",
        "information_retained": ["without-replacement dependence", "adjacent-order sensitivity"],
        "information_discarded": ["full covariance eigenvectors"],
        "context_mode": "statement_only",
        "parent_route_ids": [parent_id],
    }
    base_method_family = "standalone-self-chosen-family" if standalone else "fanout-assigned"
    if standalone:
        card["rollout_id"] = task_id
        card["method_family"] = base_method_family
    write_json(card_path, card)
    card_hash = hashlib.sha256(card_path.read_bytes()).hexdigest()
    task = {
        "schema_version": "1.0",
        "task_id": task_id,
        "title": "sealed route import fixture",
        "role": "explorer",
        "objective": "exercise controlled statement-only route import",
        "claim_ids": [],
        "dependencies": [],
        "inputs": [],
        "allowed_max_evidence": "E3",
        "required_artifacts": [],
        "acceptance_checks": [],
        "verifiers": [],
        "research_mode": "sealed_breadth",
        "context_policy": {
            "mode": "statement_only",
            "allowlist": [],
            "denylist": [],
            "reveal_after_route_card": True,
        },
        "method_constraints": {
            "method_family": base_method_family,
            "required_differences": [],
            "forbidden_methods": [],
            "required_controls": [],
        },
        "rollout_strategy": {
            "route_card_minutes": 20,
            "immutable_route_card": True,
        },
        "route_ids": [parent_id],
        "strict_claim_scope": True,
        "budget_hint": {"mode": "breadth", "checkpoint_minutes": 30},
        "status": "ready",
    }
    if not standalone:
        task["fanout_manifest"] = "research/fanouts/T900-sealed-import.json"
    write_json(run_dir / "task.json", task)
    write_json(root / "research" / "tasks" / f"{task_id}.json", task)
    if not standalone:
        write_json(manifest_path, manifest)
    avenue = {
        "name": "locked coupling route",
        "objective": "Test the locked exchangeable-pair RPCD route.",
        "outcome": "The route remains open after its first exact controls.",
        "status": "open",
        "method_family": card["method_family"],
        "representation": card["representation"],
        "state_or_invariant": card["state_or_invariant"],
        "core_candidate_lemma": card["core_candidate_lemma"],
        "predicted_failure": card["predicted_failure"],
        "falsifier": card["falsifier"],
        "target_implication": card["target_implication"],
        "information_retained": card["information_retained"],
        "information_discarded": card["information_discarded"],
        "context_mode": "statement_only",
        "parent_route_ids": card["parent_route_ids"],
        "decision": "deepen",
    }
    write_json(
        run_dir / "result.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "worker": "standalone-sealed-worker" if standalone else strategy["worker"],
            "artifacts": [{"path": card_path.relative_to(root).as_posix()}],
            "iteration": {"avenues": [avenue]},
        },
    )
    final_validation_path = run_dir / "validation.json"
    write_json(final_validation_path, {"valid": True, "errors": []})
    phase_result = run_dir / "phase-001-result.json"
    write_json(phase_result, {"schema_version": "1.0", "task_id": task_id})
    validation_path = run_dir / "phase-001-validation.json"
    write_json(validation_path, {"valid": True, "errors": []})
    invocation = {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": run_id,
        "worker": "standalone-sealed-worker" if standalone else strategy["worker"],
        "dry_run": False,
        "iteration_complete": True,
        "active_research_seconds": 7200.0,
        "exit_code": 0,
        "research_mode": "sealed_breadth",
        "context_policy": {"mode": "statement_only"},
        "rollout_strategy": None if standalone else strategy,
        "repository_source_snapshot": repository_source_snapshot(root, task),
        "cwd": str(root.resolve()),
        "preflight_verifiers": {
            "path": (run_dir / "trusted_verifiers.preflight.json").relative_to(root).as_posix(),
            "status": "not_configured",
            "valid": True,
        },
        "route_card": {
            "path": card_path.relative_to(root).as_posix(),
            "sha256": card_hash,
        },
        "route_card_sha256": card_hash,
        "phases": [
            {
                "phase": 1,
                "phase_kind": "sealed_route_card",
                "result": phase_result.relative_to(root).as_posix(),
                "active_seconds": 7200.0,
                "exit_code": 0,
            }
        ],
    }
    invocation_path = run_dir / "invocation.json"
    write_json(invocation_path, invocation)
    write_empty_trusted_reports(root, run_dir, task_id)
    write_artifact_manifest(root, run_dir, task_id)

    second_run_dir = root / "runs" / task_id / "run-agent-002"
    second_invocation = {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": second_run_dir.name,
        "worker": second_strategy["worker"],
        "dry_run": False,
        "iteration_complete": True,
        "active_research_seconds": 7200.0,
        "exit_code": 0,
        "rollout_strategy": second_strategy,
        "repository_source_snapshot": repository_source_snapshot(root, task),
        "cwd": str(root.resolve()),
        "preflight_verifiers": {
            "path": (second_run_dir / "trusted_verifiers.preflight.json")
            .relative_to(root)
            .as_posix(),
            "status": "not_configured",
            "valid": True,
        },
        "phases": [
            {
                "phase": 1,
                "phase_kind": "research",
                "active_seconds": 7200.0,
                "exit_code": 0,
            }
        ],
    }
    second_result = {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": second_run_dir.name,
        "worker": second_strategy["worker"],
        "artifacts": [],
    }
    second_validation = {"valid": True, "errors": []}
    write_json(second_run_dir / "invocation.json", second_invocation)
    write_json(second_run_dir / "task.json", task)
    write_json(second_run_dir / "validation.json", second_validation)
    write_json(second_run_dir / "result.json", second_result)
    write_empty_trusted_reports(root, second_run_dir, task_id)
    write_artifact_manifest(root, second_run_dir, task_id)
    ensemble_path = (
        root / "runs" / task_id / "ensembles" / "ensemble-fixture" / "ensemble.json"
    )
    primary_attestation = None
    secondary_attestation = None
    if not standalone:
        _, primary_attestation = _validated_run_attestation(
            root, task_id, strategy, run_dir
        )
        _, secondary_attestation = _validated_run_attestation(
            root, task_id, second_strategy, second_run_dir
        )
    ensemble = {
        "schema_version": "1.0",
        "kind": "rpcd-independent-rollout-ensemble",
        "ensemble_id": "ensemble-fixture",
        "task_id": task_id,
        "dry_run": False,
        "complete": True,
        "selected_rollout_ids": [strategy["rollout_id"], second_strategy["rollout_id"]],
        "distinct_method_families": sorted(
            {strategy["method_family"], second_strategy["method_family"]}
        ),
        "source_manifest": manifest_path.relative_to(root).as_posix(),
        "source_manifest_sha256": (
            hashlib.sha256(manifest_path.read_bytes()).hexdigest() if not standalone else ""
        ),
        "rollouts": [
            {
                "rollout_id": strategy["rollout_id"],
                "worker": strategy["worker"],
                "method_family": strategy["method_family"],
                "status": "completed",
                "run_dir": run_dir.relative_to(root).as_posix(),
                "run_attestation": primary_attestation,
            },
            {
                "rollout_id": second_strategy["rollout_id"],
                "worker": second_strategy["worker"],
                "method_family": second_strategy["method_family"],
                "status": "completed",
                "run_dir": second_run_dir.relative_to(root).as_posix(),
                "run_attestation": secondary_attestation,
            }
        ],
    }
    if not standalone:
        write_json(ensemble_path, ensemble)
    return {
        "card": card_path,
        "invocation": invocation_path,
        "validation": validation_path,
        "final_validation": final_validation_path,
        "ensemble": ensemble_path,
    }


def refresh_fixture_run_attestation(fixture: dict[str, Path]) -> None:
    """Refresh the primary run hashes after a test deliberately edits its result."""

    ensemble = json.loads(fixture["ensemble"].read_text(encoding="utf-8"))
    run_dir = fixture["card"].parent.parent
    invocation = json.loads((run_dir / "invocation.json").read_text(encoding="utf-8"))
    _, attestation = _validated_run_attestation(
        run_dir.parents[2],
        invocation["task_id"],
        invocation["rollout_strategy"],
        run_dir,
    )
    ensemble["rollouts"][0]["run_attestation"] = attestation
    write_json(fixture["ensemble"], ensemble)


def activate_imported_route(
    root: Path,
    route_id: str,
    *,
    reviewer_worker: str = "independent-target-reviewer",
    evidence_artifact: str | None = None,
    apply_review: bool = True,
) -> Path:
    route_file = root / "research" / "routes" / f"{route_id}.json"
    route = json.loads(route_file.read_text(encoding="utf-8"))
    task_id = "T902-route-target-review"
    run_id = f"review-run-{route_id}"
    artifact_dir = root / "runs" / task_id / run_id / "artifacts"
    evidence = artifact_dir / "target-fidelity-evidence.json"
    write_json(
        evidence,
        {
            "route_id": route_id,
            "source_card_path": route["provenance"].get("source_card_path"),
            "route_card_sha256": route["provenance"].get("route_card_hash"),
        },
    )
    review_path = artifact_dir / "review.json"
    write_json(
        review_path,
        {
            "schema_version": "1.0",
            "kind": "rpcd-route-target-review",
            "review_id": f"review-{route_id}",
            "route_id": route_id,
            "reviewer_task_id": task_id,
            "reviewer_worker": reviewer_worker,
            "reviewer_run_id": run_id,
            "source_route_sha256": hashlib.sha256(route_file.read_bytes()).hexdigest(),
            "route_card_sha256": route["provenance"]["route_card_hash"],
            "target_claim_id": route["target_claim_id"],
            "decision": "activate_scout",
            "checks": {
                "normalized_positive_definite_quadratic": True,
                "fresh_independent_permutations_each_epoch": True,
                "all_initial_points": True,
                "expectation_of_a_distance": True,
                "dimension_uniform_target_transfer": True,
                "stronger_proxy_not_treated_as_equivalent": True,
                "method_family_is_mathematically_distinct": True,
            },
            "rationale": "The locked route addresses the exact normalized C050 target and is distinct enough for one scout allocation; no lemma is certified.",
            "evidence_artifacts": [
                evidence_artifact or evidence.relative_to(root).as_posix()
            ],
            "reopen_if": [],
        },
    )
    finalize_completed_reviewer_run(
        root,
        task_id=task_id,
        run_id=run_id,
        worker=reviewer_worker,
        artifacts=[evidence, review_path],
    )
    return review_route_target(root, route_id, review_path) if apply_review else review_path


def continuation_import_fixture(root: Path) -> Path:
    task_id = "T901-continuation-import"
    run_id = "run-depth-001"
    worker = "depth-worker"
    run_dir = root / "runs" / task_id / run_id
    root_route = route_node("R100-l0-target", "L0", [], family="finite-time-target")
    parent = route_node(
        "R110-direct-parent", "L1", ["R100-l0-target"], family="direct-c050"
    )
    write_json(root / "research" / "routes" / "R100-l0-target.json", root_route)
    write_json(root / "research" / "routes" / "R110-direct-parent.json", parent)
    task = {
        "schema_version": "1.0",
        "task_id": task_id,
        "title": "continuation import fixture",
        "role": "researcher",
        "objective": "branch at the exact active RPCD frontier edge",
        "claim_ids": [],
        "dependencies": [],
        "inputs": [],
        "allowed_max_evidence": "E3",
        "required_artifacts": [],
        "acceptance_checks": [],
        "route_ids": ["R110-direct-parent"],
        "research_mode": "continuation_depth",
        "context_policy": {
            "mode": "full_history",
            "allowlist": [],
            "denylist": [],
            "reveal_after_route_card": False,
        },
        "method_constraints": {
            "method_family": "exchangeable-permutation-pairs",
            "required_differences": [],
            "forbidden_methods": [],
            "required_controls": [],
        },
        "strict_claim_scope": True,
        "verifiers": [],
        "budget_hint": {"mode": "deep", "checkpoint_minutes": 30},
        "status": "ready",
    }
    avenue = {
        "name": "adjacent coupling child",
        "objective": "repair the first conditional contraction edge",
        "outcome": "one exact adjacent child remains open",
        "status": "open",
        "route_id": "R111-coupling-child",
        "parent_route_ids": ["R110-direct-parent"],
        "method_family": "exchangeable-permutation-pairs",
        "representation": "Adjacent-transposition coupling of fresh epoch permutations.",
        "state_or_invariant": "Conditional A-energy decrement variance.",
        "core_candidate_lemma": "The coupled decrement pays a dimension-uniform mu fraction.",
        "information_retained": ["fresh epoch randomness", "coordinate order"],
        "information_discarded": ["irrelevant labeling symmetry"],
        "target_implication": "Iteration would prove the C050 expected-distance target.",
        "predicted_failure": "A frustrated cycle may lose one factor n.",
        "falsifier": "Exact rational four-cycle enumeration.",
        "first_bad_edge": "conditional variance to uniform energy decrement",
        "source_layer": "L1",
        "next_layer": "L2",
        "branch_kind": "depth",
        "decision": "deepen",
    }
    result = {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": run_id,
        "worker": worker,
        "status": "partial",
        "summary": "Produced one adjacent proposed child without claiming a proof.",
        "claims": [],
        "artifacts": [],
        "checks": [],
        "failed_attempts": ["A scalar spectral compression lost anisotropy."],
        "iteration": {
            "avenues": [avenue],
            "checkpoints": [
                {
                    "elapsed_active_minutes": minute,
                    "summary": f"checkpoint {minute}",
                    "next_action": "continue the exact adjacent route",
                }
                for minute in (30, 60, 90, 120)
            ],
            "stress_tests": ["frustrated four-cycle exact control"],
            "deepest_obstruction": "dimension-uniform conditional variance transfer",
        },
        "literature": [],
        "next_tasks": [],
        "limitations": ["The candidate lemma is unproved."],
    }
    write_json(run_dir / "task.json", task)
    write_json(run_dir / "result.json", result)
    write_json(run_dir / "validation.json", {"valid": True, "errors": []})
    write_json(
        run_dir / "invocation.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "worker": worker,
            "dry_run": False,
            "iteration_complete": True,
            "active_research_seconds": 7200.0,
            "exit_code": 0,
            "research_mode": "continuation_depth",
            "rollout_strategy": None,
            "phases": [
                {
                    "phase": 1,
                    "phase_kind": "research",
                    "active_seconds": 7200.0,
                    "exit_code": 0,
                }
            ],
        },
    )
    return run_dir / "result.json"


def write_prune_verdict(
    root: Path,
    route_id: str,
    *,
    reviewer_worker: str,
    master_claim_affected: bool = False,
) -> Path:
    route_file = root / "research" / "routes" / f"{route_id}.json"
    route = json.loads(route_file.read_text(encoding="utf-8"))
    task_id = "T903-route-prune-review"
    run_id = f"prune-run-{route_id}"
    artifact_dir = root / "runs" / task_id / run_id / "artifacts"
    certificate = artifact_dir / "exact-witness.json"
    write_json(
        certificate,
        {
            "kind": "exact-rational-counterexample",
            "route_id": route_id,
            "scope": "The route-local candidate lemma only; C050 is unaffected.",
            "arithmetic": "exact rational",
        },
    )
    verdict_path = artifact_dir / "verdict.json"
    write_json(
        verdict_path,
        {
            "schema_version": "1.0",
            "kind": "rpcd-route-prune-verdict",
            "verdict_id": f"prune-{route_id}",
            "route_id": route_id,
            "reviewer_task_id": task_id,
            "reviewer_worker": reviewer_worker,
            "reviewer_run_id": run_id,
            "source_route_sha256": hashlib.sha256(route_file.read_bytes()).hexdigest(),
            "route_card_sha256": route["provenance"]["route_card_hash"],
            "target_claim_id": route["target_claim_id"],
            "route_local_statement": route["statement"],
            "evidence_level": "E2",
            "certificate_kind": "exact_counterexample",
            "certificate_artifacts": [certificate.relative_to(root).as_posix()],
            "master_claim_affected": master_claim_affected,
            "rationale": "Independent exact rational arithmetic falsifies this sufficient route lemma only.",
        },
    )
    finalize_completed_reviewer_run(
        root,
        task_id=task_id,
        run_id=run_id,
        worker=reviewer_worker,
        artifacts=[certificate, verdict_path],
    )
    return verdict_path


def refresh_reviewer_artifact_manifest(root: Path, record_path: Path) -> None:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    run_dir = record_path.parent.parent
    write_artifact_manifest(root, run_dir, record["reviewer_task_id"])


class RouteDagTests(unittest.TestCase):
    def test_valid_five_layer_rpcd_route_dag(self) -> None:
        self.assertEqual(validate_route_dag(layered_routes()), [])

    def test_continuation_must_branch_from_exact_active_frontier_and_adjacent_layer(self) -> None:
        root = route_node("R100", "L0", [], family="finite-time-target")
        parent = route_node("R110", "L1", ["R100"], family="direct-c050")
        avenue = {
            "route_id": "R111-adjacent-child",
            "parent_route_ids": ["R110"],
            "method_family": "exchangeable-permutation-pairs",
            "representation": "An adjacent-transposition coupling of epoch permutations.",
            "state_or_invariant": "Conditional A-energy decrement variance.",
            "core_candidate_lemma": "The coupled decrement pays a dimension-uniform fraction of mu.",
            "information_retained": ["fresh epoch permutations"],
            "information_discarded": ["within-epoch path after conditioning"],
            "target_implication": "Iterating this conditional contraction would prove C050.",
            "predicted_failure": "An anisotropic cycle may lose one factor n.",
            "falsifier": "Exact rational enumeration on the smallest frustrated cycle.",
            "first_bad_edge": "conditional variance to uniform energy decrement",
            "source_layer": "L1",
            "next_layer": "L2",
            "branch_kind": "depth",
            "decision": "deepen",
        }
        self.assertEqual(validate_continuation_avenue([root, parent], "R110", avenue), [])

        wrong_parent = deepcopy(avenue)
        wrong_parent["parent_route_ids"] = ["R100"]
        wrong_parent["source_layer"] = "L0"
        errors = validate_continuation_avenue([root, parent], "R110", wrong_parent)
        self.assertTrue(any("exact one-element" in error for error in errors))
        self.assertTrue(any("source_layer" in error for error in errors))

        child = route_node("R120", "L2", ["R110"], family="existing-depth")
        errors = validate_continuation_avenue([root, parent, child], "R110", avenue)
        self.assertTrue(any("not a current active frontier" in error for error in errors))

    def test_parent_must_be_in_immediately_preceding_layer(self) -> None:
        routes = layered_routes()
        routes[-1]["parent_ids"] = ["R120"]
        errors = validate_route_dag(routes)
        self.assertTrue(any("must be in L3" in error for error in errors))

    def test_cycle_is_detected_even_when_layers_are_also_invalid(self) -> None:
        routes = layered_routes()
        routes[0]["parent_ids"] = ["R110"]
        errors = validate_route_dag(routes)
        self.assertTrue(any("cycle detected" in error for error in errors))

    def test_exact_signature_duplicates_must_be_explicitly_merged(self) -> None:
        routes = layered_routes()
        duplicate = deepcopy(routes[3])
        duplicate["route_id"] = "R131"
        routes.append(duplicate)
        self.assertEqual(find_exact_signature_duplicates(routes), [["R130", "R131"]])
        errors = validate_route_dag(routes)
        self.assertTrue(any("unresolved exact-signature duplicate" in error for error in errors))

        duplicate["status"] = "merged"
        duplicate["decision"] = "merge"
        duplicate["merge_target_id"] = "R130"
        self.assertEqual(validate_route_dag(routes), [])

    def test_merge_target_must_have_same_signature(self) -> None:
        routes = layered_routes()
        merged = deepcopy(routes[3])
        merged["route_id"] = "R131"
        merged["signature"]["core_candidate_lemma"] = "A genuinely different obligation."
        merged["status"] = "merged"
        merged["decision"] = "merge"
        merged["merge_target_id"] = "R130"
        routes.append(merged)
        errors = validate_route_dag(routes)
        self.assertTrue(any("exact same signature" in error for error in errors))

    def test_duplicate_key_ignores_failure_verifier_prose_but_namespaces_target_and_layer(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        duplicate = deepcopy(route)
        duplicate["route_id"] = "R111"
        duplicate["signature"]["known_failure_mode"] = "A different hostile objection."
        duplicate["signature"]["verifier_class"] = "A different exact verifier."
        duplicate["signature"]["representation"] = "  REPRESENTATION   r110 "
        self.assertEqual(find_exact_signature_duplicates([route, duplicate]), [["R110", "R111"]])

        different_target = deepcopy(duplicate)
        different_target["route_id"] = "R112"
        different_target["target_claim_id"] = "C051"
        self.assertEqual(find_exact_signature_duplicates([route, different_target]), [])

        different_layer = deepcopy(duplicate)
        different_layer["route_id"] = "R113"
        different_layer["layer"] = "L2"
        self.assertEqual(find_exact_signature_duplicates([route, different_layer]), [])

    def test_suspended_route_has_explicit_reopen_conditions(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        route["status"] = "suspended"
        route["decision"] = "suspend"
        route["reopen_if"] = ["C043 aggregate Schur envelope is independently reconstructed"]
        self.assertTrue(can_reopen(route, route["reopen_if"]))
        self.assertFalse(can_reopen(route, []))

        route["reopen_if"] = []
        errors = validate_route_dag([route_node("R100", "L0", []), route])
        self.assertTrue(any("requires at least one reopen condition" in error for error in errors))

    def test_coordinator_precommit_is_valid_but_not_realized_sealed_breadth(self) -> None:
        route = route_node(
            "R110",
            "L1",
            ["R100"],
            family="covariance-superoperator",
            search_mode="sealed_breadth",
        )
        route["provenance"].update(
            route_card_origin="coordinator_precommit",
            agent_rollout_id=None,
        )
        for field in (
            "agent_worker",
            "agent_run_id",
            "source_card_path",
            "source_review_path",
            "route_review_hash",
            "reviewer_task_id",
            "reviewer_worker",
            "reviewer_run_id",
            "reviewer_run_attestation",
            "independent_breadth_eligible",
            "resumed_from_checkpoint",
        ):
            route["provenance"].pop(field)
        self.assertEqual(validate_route_node(route), [])
        errors = audit_portfolio([route])
        self.assertTrue(any("no route descended from an agent-generated" in error for error in errors))

    def test_agent_generated_sealed_card_requires_rollout_identity(self) -> None:
        route = route_node("R110", "L1", ["R100"], search_mode="sealed_breadth")
        route["provenance"]["agent_rollout_id"] = None
        errors = validate_route_node(route)
        self.assertTrue(any("requires agent_rollout_id" in error for error in errors))

    def test_agent_generated_sealed_card_requires_tracked_source_path(self) -> None:
        route = route_node("R110", "L1", ["R100"], search_mode="sealed_breadth")
        route["provenance"].pop("source_card_path")
        errors = validate_route_node(route)
        self.assertTrue(any("requires source_card_path" in error for error in errors))

    def test_agent_generated_route_cannot_activate_by_manual_status_edit(self) -> None:
        route = route_node("R110", "L1", ["R100"], search_mode="sealed_breadth")
        for field in (
            "source_review_path",
            "route_review_hash",
            "reviewer_worker",
            "reviewer_run_id",
        ):
            route["provenance"].pop(field)
        errors = validate_route_node(route)
        self.assertTrue(any("controlled target review" in error for error in errors))

    def test_manual_hard_prune_without_controlled_verdict_provenance_is_invalid(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        route["status"] = "refuted"
        route["decision"] = "hard_prune"
        errors = validate_route_node(route)
        self.assertTrue(any("controlled prune provenance" in error for error in errors))


class RecommendationTests(unittest.TestCase):
    def test_score_thresholds_choose_deepen_scout_and_suspend(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        self.assertEqual(recommend_route(route), "deepen")
        route["score"].update(
            blocker_specificity=1,
            falsifiability=1,
            recent_information_gain=0,
        )
        self.assertEqual(recommend_route(route), "scout")
        route["score"].update(target_transfer=0)
        self.assertEqual(recommend_route(route), "suspend")

    def test_hard_prune_veto_overrides_high_score(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        route["status"] = "refuted"
        route["decision"] = "hard_prune"
        self.assertEqual(recommend_route(route), "suspend")

    def test_unreviewed_proposed_route_cannot_skip_scouting(self) -> None:
        route = route_node("R110", "L1", ["R100"])
        route["status"] = "proposed"
        route["decision"] = "unreviewed"
        self.assertEqual(recommend_route(route), "scout")


class PortfolioTests(unittest.TestCase):
    def test_portfolio_requires_one_active_sealed_breadth_route(self) -> None:
        active = [
            route_node("R110", "L1", ["R100"], family="bellman-schur"),
            route_node("R111", "L1", ["R100"], family="covariance-superoperator"),
        ]
        errors = audit_portfolio(active)
        self.assertTrue(any("no route descended from an agent-generated" in error for error in errors))
        active[1] = route_node(
            "R111",
            "L1",
            ["R100"],
            family="covariance-superoperator",
            search_mode="sealed_breadth",
        )
        self.assertEqual(audit_portfolio(active), [])

    def test_active_frontier_does_not_count_one_route_at_three_layers(self) -> None:
        l1 = route_node(
            "R110",
            "L1",
            ["R100"],
            family="sealed-covariance-family",
            search_mode="sealed_breadth",
        )
        l2 = route_node("R120", "L2", ["R110"], family="sealed-covariance-family")
        l3 = route_node("R130", "L3", ["R120"], family="sealed-covariance-family")
        frontier = active_frontier_routes([l1, l2, l3])
        self.assertEqual([route["route_id"] for route in frontier], ["R130"])
        self.assertEqual(audit_portfolio([l1, l2, l3]), [])

    def test_portfolio_detects_method_family_concentration(self) -> None:
        routes = [
            route_node("R110", "L1", ["R100"], family="fixed-energy-certificate"),
            route_node("R111", "L1", ["R100"], family="fixed-energy-certificate"),
            route_node(
                "R112",
                "L1",
                ["R100"],
                family="covariance-superoperator",
                search_mode="sealed_breadth",
            ),
        ]
        errors = audit_portfolio(routes)
        self.assertTrue(any("above policy cap" in error for error in errors))

    def test_portfolio_detects_stronger_certificate_concentration(self) -> None:
        routes = [
            route_node("R110", "L1", ["R100"], family="bellman"),
            route_node("R111", "L1", ["R100"], family="cycle-frame"),
            route_node("R112", "L1", ["R100"], family="shorting"),
            route_node(
                "R113",
                "L1",
                ["R100"],
                family="direct-c050",
                search_mode="sealed_breadth",
            ),
        ]
        for route in routes[:3]:
            route["target_claim_id"] = "C051"
        routes[3]["target_claim_id"] = "C050"
        errors = audit_portfolio(routes)
        self.assertTrue(any("target/certificate claim 'C051'" in error for error in errors))

    def test_route_plan_prioritizes_breadth_gate_then_preserves_depth_ties(self) -> None:
        root = route_node("R100", "L0", [], family="finite-time-target")
        root["target_claim_id"] = "C050"
        routes = [root]
        for route_id, family in (("R110", "bellman"), ("R120", "cycle"), ("R130", "shorting")):
            route = route_node(route_id, "L1", ["R100"], family=family)
            route["target_claim_id"] = "C051"
            routes.append(route)
        direct = route_node(
            "R140",
            "L1",
            ["R100"],
            family="direct-c050",
            search_mode="sealed_breadth",
        )
        direct["target_claim_id"] = "C050"
        direct["score"].update(
            counterexample_resistance=1,
            blocker_specificity=1,
            falsifiability=1,
            recent_information_gain=0,
        )
        routes.append(direct)

        concentrated_plan = plan_route_allocation(routes)
        self.assertEqual(concentrated_plan["action"], "expand_breadth")
        self.assertEqual(concentrated_plan["candidate_route_ids"], ["R100"])
        self.assertTrue(
            any(
                finding["code"] == "target_certificate_concentration"
                for finding in concentrated_plan["breadth_findings"]
            )
        )

        routes.append(
            route_node(
                "R150",
                "L1",
                ["R100"],
                family="second-direct-c050",
                search_mode="sealed_breadth",
            )
        )
        routes[-1]["target_claim_id"] = "C050"
        routes[-1]["score"].update(
            counterexample_resistance=1,
            blocker_specificity=1,
            falsifiability=1,
            recent_information_gain=0,
        )
        missing_review_plan = plan_route_allocation(routes)
        self.assertEqual(missing_review_plan["action"], "expand_breadth")
        self.assertTrue(
            any(
                finding["code"] == "missing_post_rollout_breadth_review"
                for finding in missing_review_plan["breadth_findings"]
            )
        )
        stale_planning = plan_route_allocation(
            routes,
            effective_breadth=4.0,
            breadth_review_kind="planning_estimate",
        )
        self.assertEqual(stale_planning["action"], "expand_breadth")
        self.assertTrue(
            any(
                finding["code"] == "stale_or_planning_breadth_review"
                for finding in stale_planning["breadth_findings"]
            )
        )
        depth_plan = plan_route_allocation(
            routes,
            effective_breadth=4.0,
            breadth_review_kind="post_rollout_review",
        )
        self.assertEqual(depth_plan["action"], "mixed")
        self.assertEqual(
            depth_plan["depth_candidate_route_ids"], ["R110", "R120", "R130"]
        )
        self.assertEqual(
            depth_plan["protected_scout_route_ids"], ["R140", "R150"]
        )
        self.assertEqual(
            depth_plan["candidate_route_ids"],
            ["R110", "R120", "R130", "R140", "R150"],
        )
        self.assertTrue(depth_plan["tie"])

        low_width_plan = plan_route_allocation(
            routes,
            effective_breadth=2.5,
            breadth_review_kind="post_rollout_review",
        )
        self.assertEqual(low_width_plan["action"], "expand_breadth")
        self.assertTrue(
            any(
                finding["code"] == "low_effective_breadth"
                for finding in low_width_plan["breadth_findings"]
            )
        )
        with self.assertRaisesRegex(RouteError, "effective_breadth"):
            plan_route_allocation(routes, effective_breadth=float("nan"))

    def test_optional_repository_policy_overrides_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "research").mkdir()
            (root / "research" / "portfolio_policy.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "recommendation": {"deepen_min_total": 9},
                        "portfolio": {"max_method_family_fraction": 0.75},
                    }
                ),
                encoding="utf-8",
            )
            policy = load_portfolio_policy(root)
        self.assertEqual(policy["recommendation"]["deepen_min_total"], 9)
        self.assertEqual(policy["recommendation"]["scout_min_total"], 5)
        self.assertEqual(policy["portfolio"]["max_method_family_fraction"], 0.75)
        self.assertEqual(
            policy["portfolio"]["active_statuses"],
            DEFAULT_PORTFOLIO_POLICY["portfolio"]["active_statuses"],
        )

    def test_t143_has_four_statement_only_distinct_method_rollouts(self) -> None:
        root = Path(__file__).resolve().parents[1]
        t143_tasks = list((root / "research" / "tasks").glob("T143-*.json"))
        self.assertEqual(len(t143_tasks), 1)
        task_id = t143_tasks[0].stem
        manifest = load_fanout_manifest(
            root / "research" / "fanouts" / "T143-initial-breadth.json",
            task_id=task_id,
        )
        self.assertEqual(len(manifest["rollouts"]), 4)
        self.assertEqual(
            len({rollout["method_family"] for rollout in manifest["rollouts"]}),
            4,
        )
        self.assertTrue(
            all(rollout["context_mode"] == "statement_only" for rollout in manifest["rollouts"])
        )

        task = json.loads(
            t143_tasks[0].read_text(encoding="utf-8")
        )
        self.assertEqual(
            task["context_policy"]["allowlist"],
            ["research/routes/cards/R100-finite-time-statement-only.md"],
        )
        self.assertIn("route_card.json", task["required_artifacts"])
        self.assertNotIn("immutable_route_card.json", task["required_artifacts"])

        r140 = json.loads(
            (root / "research" / "routes" / "R140-direct-covariance-multiepoch.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(r140["provenance"]["route_card_origin"], "coordinator_precommit")
        self.assertFalse(is_sealed_breadth_route(r140))
        card_bytes = (
            root / "research" / "routes" / "cards" / "R140-direct-covariance-multiepoch.md"
        ).read_bytes()
        self.assertEqual(
            hashlib.sha256(card_bytes).hexdigest(),
            r140["provenance"]["route_card_hash"],
        )


class RouteCardImportTests(unittest.TestCase):
    def test_target_review_requires_real_completed_reviewer_identity(self) -> None:
        for mutation in ("worker", "run", "incomplete"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                fixture = sealed_import_fixture(root, standalone=True)
                route_id = f"R156-review-{mutation}"
                import_route_card(root, fixture["card"], route_id)
                review_path = activate_imported_route(root, route_id, apply_review=False)
                review = json.loads(review_path.read_text(encoding="utf-8"))
                if mutation == "worker":
                    review["reviewer_worker"] = "forged-reviewer"
                    write_json(review_path, review)
                    refresh_reviewer_artifact_manifest(root, review_path)
                    expected = "reviewer_worker does not match"
                elif mutation == "run":
                    review["reviewer_run_id"] = "forged-missing-run"
                    write_json(review_path, review)
                    refresh_reviewer_artifact_manifest(root, review_path)
                    expected = "artifact of its reviewer harness run"
                else:
                    invocation_path = review_path.parent.parent / "invocation.json"
                    invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
                    invocation["iteration_complete"] = False
                    write_json(invocation_path, invocation)
                    expected = "not a canonical completed validated 120-minute run"
                with self.assertRaisesRegex(RouteError, expected):
                    review_route_target(root, route_id, review_path)

    def test_target_review_evidence_must_belong_to_attested_reviewer_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            route_id = "R157-review-artifact"
            import_route_card(root, fixture["card"], route_id)
            outside = fixture["card"].relative_to(root).as_posix()
            review_path = activate_imported_route(
                root,
                route_id,
                evidence_artifact=outside,
                apply_review=False,
            )
            with self.assertRaisesRegex(RouteError, "does not belong to the reviewer harness run"):
                review_route_target(root, route_id, review_path)

    def test_prune_requires_real_completed_reviewer_identity(self) -> None:
        for mutation in ("worker", "run", "incomplete"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                fixture = sealed_import_fixture(root, standalone=True)
                route_id = f"R158-prune-{mutation}"
                import_route_card(root, fixture["card"], route_id)
                verdict_path = write_prune_verdict(
                    root,
                    route_id,
                    reviewer_worker="independent-exact-critic",
                )
                verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
                if mutation == "worker":
                    verdict["reviewer_worker"] = "forged-reviewer"
                    write_json(verdict_path, verdict)
                    refresh_reviewer_artifact_manifest(root, verdict_path)
                    expected = "reviewer_worker does not match"
                elif mutation == "run":
                    verdict["reviewer_run_id"] = "forged-missing-run"
                    write_json(verdict_path, verdict)
                    refresh_reviewer_artifact_manifest(root, verdict_path)
                    expected = "artifact of its reviewer harness run"
                else:
                    invocation_path = verdict_path.parent.parent / "invocation.json"
                    invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
                    invocation["iteration_complete"] = False
                    write_json(invocation_path, invocation)
                    expected = "not a canonical completed validated 120-minute run"
                with self.assertRaisesRegex(RouteError, expected):
                    prune_route(root, route_id, verdict_path)

    def test_prune_certificate_must_belong_to_attested_reviewer_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            route_id = "R159-prune-artifact"
            import_route_card(root, fixture["card"], route_id)
            verdict_path = write_prune_verdict(
                root,
                route_id,
                reviewer_worker="independent-exact-critic",
            )
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
            verdict["certificate_artifacts"] = [fixture["card"].relative_to(root).as_posix()]
            write_json(verdict_path, verdict)
            refresh_reviewer_artifact_manifest(root, verdict_path)
            with self.assertRaisesRegex(RouteError, "does not belong to the reviewer harness run"):
                prune_route(root, route_id, verdict_path)

    def test_route_review_rejects_windows_hostile_recorded_paths(self) -> None:
        hostile_paths = (
            "research/routes/cards/card.json:alternate-stream",
            "research/routes/cards/CON.json",
            "research/routes/cards/trailing.",
            "research/routes/cards/trailing ",
            "research/routes/cards/../escape.json",
            "research/routes/cards/control\x01.json",
        )
        for index, hostile_path in enumerate(hostile_paths):
            with self.subTest(path=hostile_path), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                fixture = sealed_import_fixture(root, standalone=True)
                import_route_card(root, fixture["card"], f"R15{index}-hostile-review")
                with self.assertRaisesRegex(RouteError, "safe repository-relative path"):
                    activate_imported_route(
                        root,
                        f"R15{index}-hostile-review",
                        evidence_artifact=hostile_path,
                    )

    def test_route_prune_rejects_windows_hostile_certificate_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            import_route_card(root, fixture["card"], "R159-hostile-prune")
            verdict_path = write_prune_verdict(
                root,
                "R159-hostile-prune",
                reviewer_worker="independent-exact-critic",
            )
            verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
            verdict["certificate_artifacts"] = [
                "runs/route-prune/R159-hostile-prune/witness.json:certificate"
            ]
            write_json(verdict_path, verdict)
            refresh_reviewer_artifact_manifest(root, verdict_path)
            with self.assertRaisesRegex(RouteError, "safe repository-relative path"):
                prune_route(root, "R159-hostile-prune", verdict_path)

    def test_hard_prune_requires_independent_e2_route_local_exact_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            output = import_route_card(root, fixture["card"], "R150-prune-gate")
            route = json.loads(output.read_text(encoding="utf-8"))

            self_verdict = write_prune_verdict(
                root,
                "R150-prune-gate",
                reviewer_worker=route["provenance"]["agent_worker"],
            )
            with self.assertRaisesRegex(RouteError, "independent"):
                prune_route(root, "R150-prune-gate", self_verdict)

            master_verdict = write_prune_verdict(
                root,
                "R150-prune-gate",
                reviewer_worker="independent-exact-critic",
                master_claim_affected=True,
            )
            with self.assertRaisesRegex(RouteError, "master_claim_affected=false"):
                prune_route(root, "R150-prune-gate", master_verdict)

            verdict = write_prune_verdict(
                root,
                "R150-prune-gate",
                reviewer_worker="independent-exact-critic",
            )
            prune_route(root, "R150-prune-gate", verdict)
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual((route["status"], route["decision"]), ("refuted", "hard_prune"))
            self.assertEqual(route["provenance"]["prune_evidence_level"], "E2")
            self.assertEqual(
                route["provenance"]["prune_certificate_kind"], "exact_counterexample"
            )
            self.assertEqual(validate_route_dag(load_route_nodes(root)), [])

            tracked_certificate = root / route["provenance"]["prune_certificate_artifacts"][0][
                "path"
            ]
            original_certificate = tracked_certificate.read_bytes()
            tracked_certificate.write_bytes(original_certificate + b" ")
            errors = audit_route_repository(root)
            self.assertTrue(
                any("tracked prune certificate SHA-256" in error for error in errors)
            )
            tracked_certificate.write_bytes(original_certificate)

            tracked = root / route["provenance"]["source_prune_path"]
            tracked.write_text(tracked.read_text(encoding="utf-8") + " ", encoding="utf-8")
            errors = audit_route_repository(root)
            self.assertTrue(any("tracked prune verdict SHA-256" in error for error in errors))

    def test_controlled_continuation_import_creates_only_proposed_adjacent_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result_path = continuation_import_fixture(root)
            output = import_continuation_result(root, result_path)
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(route["parent_ids"], ["R110-direct-parent"])
            self.assertEqual(route["layer"], "L2")
            self.assertEqual((route["status"], route["decision"]), ("proposed", "unreviewed"))
            self.assertEqual(
                route["provenance"]["source_result_path"],
                "research/routes/results/R111-coupling-child.json",
            )
            self.assertEqual(validate_route_dag(load_route_nodes(root)), [])

    def test_resumed_continuation_is_recorded_as_depth_not_independent_breadth(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result_path = continuation_import_fixture(root)
            invocation_path = result_path.parent / "invocation.json"
            invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
            invocation["resume_lineage"] = {
                "independence": False,
                "eligible_for_fanout": False,
                "checkpoint": "research/checkpoints/T901--run-depth-000.json",
            }
            write_json(invocation_path, invocation)

            output = import_continuation_result(root, result_path)
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(route["provenance"]["resumed_from_checkpoint"])
            self.assertFalse(route["provenance"]["independent_breadth_eligible"])
            self.assertFalse(is_sealed_breadth_route(route))
            self.assertEqual(validate_route_dag(load_route_nodes(root)), [])

    def test_completed_agent_card_requires_independent_review_before_active_scout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            output = import_route_card(root, fixture["card"].relative_to(root), "R150-coupling")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(route["layer"], "L1")
            self.assertEqual((route["status"], route["decision"]), ("proposed", "unreviewed"))
            self.assertEqual(route["parent_ids"], ["R100-l0-target"])
            self.assertEqual(
                route["signature"]["state_or_invariant"],
                "Conditional variance of the A-energy decrement under the coupled pair.",
            )
            self.assertEqual(route["provenance"]["route_card_origin"], "agent_generated")
            self.assertEqual(route["provenance"]["agent_rollout_id"], "coupling-rollout")
            self.assertEqual(
                route["provenance"]["source_card_path"],
                "research/routes/cards/R150-coupling.json",
            )
            self.assertTrue((root / route["provenance"]["source_card_path"]).is_file())
            self.assertEqual(validate_route_dag(load_route_nodes(root)), [])
            self.assertTrue(audit_portfolio(load_route_nodes(root)))
            activate_imported_route(root, "R150-coupling")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual((route["status"], route["decision"]), ("active", "scout"))
            self.assertTrue(is_sealed_breadth_route(route))
            self.assertEqual(audit_portfolio(load_route_nodes(root)), [])
            self.assertEqual(audit_route_repository(root), [])
            with self.assertRaisesRegex(RouteError, "refusing to overwrite"):
                import_route_card(root, fixture["card"], "R150-coupling")

    def test_completed_standalone_sealed_card_imports_without_ensemble(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            self.assertFalse(fixture["ensemble"].exists())
            output = import_route_card(root, fixture["card"], "R150-standalone")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(route["method_family"], "standalone-self-chosen-family")
            self.assertEqual(route["provenance"]["agent_rollout_id"], "T900-sealed-import")
            self.assertEqual((route["status"], route["decision"]), ("proposed", "unreviewed"))
            activate_imported_route(root, "R150-standalone")
            self.assertEqual(audit_portfolio(load_route_nodes(root)), [])

    def test_checkpoint_resume_cannot_be_imported_as_independent_sealed_breadth(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            invocation = json.loads(fixture["invocation"].read_text(encoding="utf-8"))
            invocation["resume_lineage"] = {
                "independence": False,
                "eligible_for_fanout": False,
                "checkpoint": "research/checkpoints/T900--prior.json",
            }
            write_json(fixture["invocation"], invocation)
            with self.assertRaisesRegex(RouteError, "cannot be imported as independent sealed breadth"):
                import_route_card(root, fixture["card"], "R150-resumed")

    def test_resume_lineage_cannot_claim_independence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result_path = continuation_import_fixture(root)
            invocation_path = result_path.parent / "invocation.json"
            invocation = json.loads(invocation_path.read_text(encoding="utf-8"))
            invocation["resume_lineage"] = {
                "independence": True,
                "eligible_for_fanout": False,
            }
            write_json(invocation_path, invocation)
            with self.assertRaisesRegex(RouteError, "independence=false"):
                import_continuation_result(root, result_path)

    def test_import_rejects_card_changed_after_locked_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            fixture["card"].write_text(
                fixture["card"].read_text(encoding="utf-8") + " ", encoding="utf-8"
            )
            with self.assertRaisesRegex(RouteError, "SHA-256"):
                import_route_card(root, fixture["card"], "R150-tampered")
            self.assertFalse((root / "research" / "routes" / "R150-tampered.json").exists())

    def test_import_rejects_final_avenue_that_changes_any_locked_mathematical_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            result_path = fixture["card"].parent.parent / "result.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["iteration"]["avenues"][0]["predicted_failure"] = (
                "A different post-reveal failure story."
            )
            write_json(result_path, result)
            refresh_fixture_run_attestation(fixture)
            with self.assertRaisesRegex(RouteError, "locked fields changed.*predicted_failure"):
                import_route_card(root, fixture["card"], "R150-mutated-avenue")

    def test_imported_route_cannot_self_review_into_active_portfolio(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            import_route_card(root, fixture["card"], "R150-self-review")
            route = json.loads(
                (root / "research" / "routes" / "R150-self-review.json").read_text(
                    encoding="utf-8"
                )
            )
            with self.assertRaisesRegex(RouteError, "independent"):
                activate_imported_route(
                    root,
                    "R150-self-review",
                    reviewer_worker=route["provenance"]["agent_worker"],
                )

    def test_import_rejects_unvalidated_or_unlinked_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root, standalone=True)
            invocation = json.loads(fixture["invocation"].read_text(encoding="utf-8"))
            invocation["phases"] = []
            write_json(fixture["invocation"], invocation)
            with self.assertRaisesRegex(RouteError, "phase timing"):
                import_route_card(root, fixture["card"], "R150-no-time-lineage")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            write_json(fixture["validation"], {"valid": False, "errors": ["bad card"]})
            with self.assertRaisesRegex(RouteError, "validation.valid"):
                import_route_card(root, fixture["card"], "R150-invalid")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            write_json(
                fixture["final_validation"],
                {"valid": False, "errors": ["trusted final verifier failed"]},
            )
            with self.assertRaisesRegex(RouteError, "final validation.valid"):
                import_route_card(root, fixture["card"], "R150-final-invalid")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            fixture["ensemble"].unlink()
            with self.assertRaisesRegex(RouteError, "ensemble lineage"):
                import_route_card(root, fixture["card"], "R150-unlinked")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            ensemble = json.loads(fixture["ensemble"].read_text(encoding="utf-8"))
            ensemble["rollouts"][0]["run_attestation"]["result_sha256"] = "0" * 64
            write_json(fixture["ensemble"], ensemble)
            with self.assertRaisesRegex(RouteError, "atomic rollout validation"):
                import_route_card(root, fixture["card"], "R150-unattested")

    def test_import_ignores_incomplete_shard_when_complete_merged_ensemble_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            shard = json.loads(fixture["ensemble"].read_text(encoding="utf-8"))
            shard["ensemble_id"] = "ensemble-shard"
            shard["complete"] = False
            shard["rollouts"] = shard["rollouts"][:1]
            shard_path = (
                fixture["ensemble"].parent.parent
                / "ensemble-shard"
                / "ensemble.json"
            )
            write_json(shard_path, shard)
            output = import_route_card(root, fixture["card"], "R150-merged-lineage")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual((route["status"], route["decision"]), ("proposed", "unreviewed"))

    def test_import_maps_refuted_and_blocked_card_verdicts_without_false_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            result = json.loads((fixture["card"].parent.parent / "result.json").read_text(encoding="utf-8"))
            result["iteration"]["avenues"][0].update(status="refuted", decision="prune")
            write_json(fixture["card"].parent.parent / "result.json", result)
            refresh_fixture_run_attestation(fixture)
            output = import_route_card(root, fixture["card"], "R150-refuted")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual((route["status"], route["decision"]), ("suspended", "suspend"))
            self.assertEqual(len(route["reopen_if"]), 1)
            self.assertIn("independent critic", route["reopen_if"][0])
            self.assertIn("E2+", route["reopen_if"][0])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            result = json.loads((fixture["card"].parent.parent / "result.json").read_text(encoding="utf-8"))
            result["iteration"]["avenues"][0].update(status="blocked", decision="suspend")
            write_json(fixture["card"].parent.parent / "result.json", result)
            refresh_fixture_run_attestation(fixture)
            output = import_route_card(root, fixture["card"], "R150-blocked")
            route = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual((route["status"], route["decision"]), ("proposed", "unreviewed"))
            self.assertFalse(route["reopen_if"])

    def test_route_audit_rehashes_the_tracked_agent_card(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            output = import_route_card(root, fixture["card"], "R150-audited")
            route = json.loads(output.read_text(encoding="utf-8"))
            tracked = root / route["provenance"]["source_card_path"]
            tracked.write_text(tracked.read_text(encoding="utf-8") + " ", encoding="utf-8")
            errors = audit_route_repository(root)
            self.assertTrue(any("tracked source card SHA-256" in error for error in errors))

    def test_import_rejects_coordinator_card(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = sealed_import_fixture(root)
            card = json.loads(fixture["card"].read_text(encoding="utf-8"))
            card["route_card_origin"] = "coordinator_precommit"
            write_json(fixture["card"], card)
            with self.assertRaisesRegex(RouteError, "coordinator_precommit"):
                import_route_card(root, fixture["card"], "R150-coordinator")

    def test_cli_exposes_controlled_route_card_import(self) -> None:
        self.assertEqual(build_parser().parse_args(["route-plan"]).command, "route-plan")
        parsed_plan = build_parser().parse_args(
            ["route-plan", "--breadth-snapshot", "research/breadth_reviews/current.json"]
        )
        self.assertEqual(
            parsed_plan.breadth_snapshot,
            Path("research/breadth_reviews/current.json"),
        )
        args = build_parser().parse_args(
            ["route-import-card", "runs/T900/run/artifacts/route_card.json", "--route-id", "R150"]
        )
        self.assertEqual(args.command, "route-import-card")
        self.assertEqual(args.route_id, "R150")
        continuation = build_parser().parse_args(
            ["route-import-continuation", "runs/T140/run/result.json", "--avenue-index", "1"]
        )
        self.assertEqual(continuation.command, "route-import-continuation")
        self.assertEqual(continuation.avenue_index, 1)
        review = build_parser().parse_args(
            ["route-review-target", "R150", "runs/reviews/R150/review.json"]
        )
        self.assertEqual(review.command, "route-review-target")
        prune = build_parser().parse_args(
            ["route-prune", "R150", "runs/prune/R150/verdict.json"]
        )
        self.assertEqual(prune.command, "route-prune")


if __name__ == "__main__":
    unittest.main()
