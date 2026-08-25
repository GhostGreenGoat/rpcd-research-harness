"""RPCD-specific route DAG validation and portfolio decisions.

The route DAG records *mathematical search routes*, not model responses.  Its
layers deliberately separate the finite-time target from major proof
representations, their first unresolved bridges, repair/closure obligations,
and executable tests::

    L0 target -> L1 representation/architecture -> L2 unresolved bridge
              -> L3 repair/atomic closure -> L4 test/certificate

This module is independent of the legacy task/result protocol.  A repository
without ``research/routes`` or ``research/portfolio_policy.json`` continues to
work; callers opt into the route system explicitly.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence


LAYERS = ("L0", "L1", "L2", "L3", "L4")
LAYER_INDEX = {layer: index for index, layer in enumerate(LAYERS)}

ROUTE_STATUSES = {
    "proposed",
    "active",
    "suspended",
    "refuted",
    "merged",
    "completed",
}
ROUTE_DECISIONS = {
    "unreviewed",
    "advance",
    "branch",
    "deepen",
    "scout",
    "suspend",
    "hard_prune",
    "merge",
    "complete",
}
SEARCH_MODES = {"sealed_breadth", "inherited_depth", "adversarial", "verification"}
ROUTE_CARD_ORIGINS = {"coordinator_precommit", "agent_generated"}
CONTEXT_MODES = {
    "statement_only",
    "statement_plus_failure_map",
    "full_repository",
    "continuation",
}

SIGNATURE_FIELDS = (
    "representation",
    "state_or_invariant",
    "core_candidate_lemma",
    "information_retained",
    "information_discarded",
    "target_implication",
    "known_failure_mode",
    "verifier_class",
)
SIGNATURE_LIST_FIELDS = {"information_retained", "information_discarded"}

# A route is a mathematical avenue, not a particular falsifier implementation.
# Duplicate detection therefore uses only the normalized mathematical core.  The
# layer and target claim namespace that core so an L2 bridge cannot be forced to
# merge with an L3 closure, or a C050 route with the stronger C051 certificate.
DUPLICATE_SIGNATURE_FIELDS = (
    "representation",
    "state_or_invariant",
    "core_candidate_lemma",
    "target_implication",
)

SCORE_FIELDS = (
    "target_transfer",
    "counterexample_resistance",
    "blocker_specificity",
    "falsifiability",
    "recent_information_gain",
)

INDEPENDENT_REFUTATION_REOPEN = (
    "An independent critic resolves the self-reported obstruction at E2+: an exact or "
    "certified counterexample sends the locked route to controlled hard-prune, while an "
    "exact rejection of that counterexample permits active reconsideration."
)

ROUTE_ID_PATTERN = re.compile(r"^R[0-9]{3,}(?:-[a-z0-9-]+)?$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

TARGET_REVIEW_CHECKS = (
    "normalized_positive_definite_quadratic",
    "fresh_independent_permutations_each_epoch",
    "all_initial_points",
    "expectation_of_a_distance",
    "dimension_uniform_target_transfer",
    "stronger_proxy_not_treated_as_equivalent",
    "method_family_is_mathematically_distinct",
)
PRUNE_EVIDENCE_LEVELS = {"E2", "E3", "E4", "E5", "E6"}
PRUNE_CERTIFICATE_KINDS = {"exact_counterexample", "certified_counterexample"}
RUN_ATTESTATION_FIELDS = {
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

# A sealed result is allowed to interpret the locked card, but not to mutate
# its mathematical avenue after inherited context is revealed.  These are all
# mathematical/context/lineage fields in route-card.schema.json; equality is
# deliberately byte-level JSON equality (including list order), not fuzzy or
# typography-normalized equality.
SEALED_CARD_AVENUE_FIELDS = (
    "method_family",
    "representation",
    "state_or_invariant",
    "core_candidate_lemma",
    "predicted_failure",
    "falsifier",
    "target_implication",
    "information_retained",
    "information_discarded",
    "context_mode",
    "parent_route_ids",
)

CONTINUATION_AVENUE_FIELDS = (
    "route_id",
    "parent_route_ids",
    "method_family",
    "representation",
    "state_or_invariant",
    "core_candidate_lemma",
    "information_retained",
    "information_discarded",
    "target_implication",
    "predicted_failure",
    "falsifier",
    "first_bad_edge",
    "source_layer",
    "next_layer",
    "branch_kind",
    "decision",
)


DEFAULT_PORTFOLIO_POLICY: dict[str, Any] = {
    "schema_version": "1.0",
    "recommendation": {
        "deepen_min_total": 8,
        "scout_min_total": 5,
        "mandatory_positive": ["target_transfer", "counterexample_resistance"],
    },
    "portfolio": {
        "active_statuses": ["active"],
        "layers": ["L1", "L2", "L3"],
        "require_sealed_breadth": True,
        "max_method_family_fraction": 0.6,
        "max_limited_target_claim_fraction": 0.6,
        "concentration_limited_target_claim_ids": ["C051"],
        "concentration_min_routes": 3,
        "min_effective_breadth": 3.0,
    },
}


class RouteError(ValueError):
    """Raised when route data or a portfolio policy cannot be loaded."""


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list_errors(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{label} must be an array"]
    errors = [
        f"{label}[{index}] must be a nonempty string"
        for index, item in enumerate(value)
        if not _is_nonempty_string(item)
    ]
    if all(isinstance(item, str) for item in value) and len(value) != len(set(value)):
        errors.append(f"{label} must not contain duplicates")
    return errors


def _deep_merge_defaults(defaults: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(defaults))
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, Mapping):
            result[key] = _deep_merge_defaults(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def validate_portfolio_policy(policy: Mapping[str, Any]) -> list[str]:
    """Return validation errors for an RPCD breadth/depth portfolio policy."""

    errors: list[str] = []
    if policy.get("schema_version") != "1.0":
        errors.append("unsupported portfolio policy schema version")

    recommendation = policy.get("recommendation")
    if not isinstance(recommendation, Mapping):
        errors.append("portfolio policy recommendation must be an object")
    else:
        deepen = recommendation.get("deepen_min_total")
        scout = recommendation.get("scout_min_total")
        if not isinstance(deepen, int) or isinstance(deepen, bool) or not 0 <= deepen <= 10:
            errors.append("recommendation.deepen_min_total must be an integer in [0, 10]")
        if not isinstance(scout, int) or isinstance(scout, bool) or not 0 <= scout <= 10:
            errors.append("recommendation.scout_min_total must be an integer in [0, 10]")
        if isinstance(deepen, int) and isinstance(scout, int) and deepen < scout:
            errors.append("deepen_min_total must be at least scout_min_total")
        mandatory = recommendation.get("mandatory_positive")
        if not isinstance(mandatory, list) or not mandatory:
            errors.append("recommendation.mandatory_positive must be a nonempty array")
        elif any(field not in SCORE_FIELDS for field in mandatory):
            errors.append("recommendation.mandatory_positive contains an unknown score field")

    portfolio = policy.get("portfolio")
    if not isinstance(portfolio, Mapping):
        errors.append("portfolio policy portfolio must be an object")
    else:
        active_statuses = portfolio.get("active_statuses")
        if not isinstance(active_statuses, list) or not active_statuses:
            errors.append("portfolio.active_statuses must be a nonempty array")
        elif any(status not in ROUTE_STATUSES for status in active_statuses):
            errors.append("portfolio.active_statuses contains an unknown route status")
        layers = portfolio.get("layers")
        if not isinstance(layers, list) or not layers:
            errors.append("portfolio.layers must be a nonempty array")
        elif any(layer not in LAYER_INDEX for layer in layers):
            errors.append("portfolio.layers contains an unknown route layer")
        if not isinstance(portfolio.get("require_sealed_breadth"), bool):
            errors.append("portfolio.require_sealed_breadth must be boolean")
        maximum = portfolio.get("max_method_family_fraction")
        if (
            not isinstance(maximum, (int, float))
            or isinstance(maximum, bool)
            or not 0.0 < float(maximum) <= 1.0
        ):
            errors.append("portfolio.max_method_family_fraction must be in (0, 1]")
        target_maximum = portfolio.get("max_limited_target_claim_fraction")
        if (
            not isinstance(target_maximum, (int, float))
            or isinstance(target_maximum, bool)
            or not 0.0 < float(target_maximum) <= 1.0
        ):
            errors.append("portfolio.max_limited_target_claim_fraction must be in (0, 1]")
        limited_claims = portfolio.get("concentration_limited_target_claim_ids")
        if not isinstance(limited_claims, list):
            errors.append("portfolio.concentration_limited_target_claim_ids must be an array")
        elif any(not _is_nonempty_string(claim_id) for claim_id in limited_claims):
            errors.append(
                "portfolio.concentration_limited_target_claim_ids must contain nonempty strings"
            )
        elif len(limited_claims) != len(set(limited_claims)):
            errors.append(
                "portfolio.concentration_limited_target_claim_ids must not contain duplicates"
            )
        minimum = portfolio.get("concentration_min_routes")
        if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
            errors.append("portfolio.concentration_min_routes must be an integer >= 1")
        minimum_breadth = portfolio.get("min_effective_breadth")
        if (
            not isinstance(minimum_breadth, (int, float))
            or isinstance(minimum_breadth, bool)
            or not math.isfinite(float(minimum_breadth))
            or float(minimum_breadth) <= 0.0
        ):
            errors.append("portfolio.min_effective_breadth must be a finite number > 0")
    return errors


def load_portfolio_policy(root: Path) -> dict[str, Any]:
    """Load ``research/portfolio_policy.json``, filling omitted keys with defaults."""

    path = Path(root) / "research" / "portfolio_policy.json"
    override: dict[str, Any] = {}
    if path.is_file():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RouteError(f"cannot read portfolio policy {path}: {error}") from error
        if not isinstance(loaded, dict):
            raise RouteError(f"expected a JSON object in {path}")
        override = loaded
    policy = _deep_merge_defaults(DEFAULT_PORTFOLIO_POLICY, override)
    errors = validate_portfolio_policy(policy)
    if errors:
        raise RouteError("invalid portfolio policy: " + "; ".join(errors))
    return policy


def load_route_nodes(root: Path, relative_directory: str = "research/routes") -> list[dict[str, Any]]:
    """Load route-node JSON files without requiring the directory to exist."""

    directory = Path(root) / relative_directory
    if not directory.is_dir():
        return []
    nodes: list[dict[str, Any]] = []
    for path in sorted(directory.glob("R*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RouteError(f"cannot read route node {path}: {error}") from error
        if not isinstance(value, dict):
            raise RouteError(f"expected a JSON object in {path}")
        nodes.append(value)
    return nodes


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RouteError(f"cannot read {label} {path}: {error}") from error
    if not isinstance(value, dict):
        raise RouteError(f"expected a JSON object in {label} {path}")
    return value


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise RouteError(f"cannot hash {path}: {error}") from error
    return digest.hexdigest()


def _validated_active_research_time(root: Path, invocation: Mapping[str, Any]) -> float:
    """Return attested active seconds when phase records exactly sum to the scalar."""

    active_seconds = invocation.get("active_research_seconds")
    phases = invocation.get("phases")
    if (
        not isinstance(active_seconds, (int, float))
        or isinstance(active_seconds, bool)
        or not math.isfinite(float(active_seconds))
        or not isinstance(phases, list)
        or not phases
    ):
        raise RouteError("completed run has no finite nonempty phase timing record")
    phase_seconds: list[float] = []
    for index, phase in enumerate(phases, start=1):
        seconds = phase.get("active_seconds") if isinstance(phase, Mapping) else None
        exit_code = phase.get("exit_code") if isinstance(phase, Mapping) else None
        if (
            not isinstance(phase, Mapping)
            or phase.get("phase") != index
            or not isinstance(seconds, (int, float))
            or isinstance(seconds, bool)
            or not math.isfinite(float(seconds))
            or float(seconds) < 0.0
            or not isinstance(exit_code, int)
            or isinstance(exit_code, bool)
            or exit_code != 0
        ):
            raise RouteError("completed run has malformed or failed phase timing lineage")
        phase_seconds.append(float(seconds))
    if not math.isclose(
        math.fsum(phase_seconds), float(active_seconds), rel_tol=1e-12, abs_tol=1e-6
    ):
        raise RouteError("completed run phase times do not sum to active_research_seconds")
    from .protocol import load_iteration_policy

    minimum = 60.0 * load_iteration_policy(root)["minimum_active_minutes_per_worker"]
    if float(active_seconds) + 1e-6 < minimum:
        raise RouteError(
            f"completed run active research time {float(active_seconds) / 60.0:.2f} minutes "
            f"is below the repository floor {minimum / 60.0:.0f} minutes"
        )
    return float(active_seconds)


def _is_checkpoint_resume(invocation: Mapping[str, Any]) -> bool:
    """Validate and identify non-independent checkpoint-resume lineage.

    A resumed process can be useful for depth, but it is not a new mathematical
    sample.  The adapter therefore has to attest both relevant negative flags;
    a malformed or independence-claiming resume record is rejected instead of
    being silently treated as a fresh run.
    """

    resume_lineage = invocation.get("resume_lineage")
    if resume_lineage is None:
        return False
    if not isinstance(resume_lineage, Mapping):
        raise RouteError("invocation.resume_lineage must be an object or null")
    if resume_lineage.get("independence") is not False:
        raise RouteError(
            "checkpoint-resume lineage must attest independence=false"
        )
    if resume_lineage.get("eligible_for_fanout") is not False:
        raise RouteError(
            "checkpoint-resume lineage must attest eligible_for_fanout=false"
        )
    return True


def _recorded_repo_path(root: Path, raw: Any, label: str) -> Path:
    if (
        not isinstance(raw, str)
        or not raw.strip()
        or any(ord(character) < 32 for character in raw)
        or ":" in raw
    ):
        raise RouteError(f"{label} must be a safe repository-relative path")
    normalized = raw.replace("\\", "/")
    portable = PurePosixPath(normalized)
    windows_path = PureWindowsPath(raw)
    unsafe_part = any(
        ":" in part
        or part[-1:] in {" ", "."}
        or any(ord(character) < 32 for character in part)
        for part in portable.parts
    )
    if (
        not portable.parts
        or portable.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or bool(windows_path.anchor)
        or ".." in portable.parts
        or windows_path.is_reserved()
        or unsafe_part
    ):
        raise RouteError(f"{label} must be a safe repository-relative path")
    candidate = Path(portable.as_posix())
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise RouteError(f"{label} escapes the repository") from error
    return resolved


def _verified_rollout_strategy(
    root: Path,
    run_dir: Path,
    invocation: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Verify fanout lineage, or identify a legitimate standalone sealed run."""

    task_id = invocation.get("task_id")
    strategy = invocation.get("rollout_strategy")
    if strategy is None:
        # ``run-codex`` can launch one statement-only sealed task without a
        # fanout manifest. validate_route_card later enforces the standalone
        # lineage convention rollout_id=task_id and the task's base family.
        return None
    if not isinstance(strategy, dict):
        raise RouteError("rollout_strategy must be null for standalone or an object for fanout")
    for field in ("rollout_id", "worker", "method_family", "context_mode"):
        if not _is_nonempty_string(strategy.get(field)):
            raise RouteError(f"rollout_strategy.{field} must be a nonempty string")
    if strategy["context_mode"] != "statement_only":
        raise RouteError("only a statement-only agent rollout may enter the route registry")
    if invocation.get("worker") != strategy["worker"]:
        raise RouteError("invocation worker does not match agent rollout lineage")

    run_relative = run_dir.relative_to(root).as_posix()
    ensemble_root = run_dir.parent / "ensembles"
    matches: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    if ensemble_root.is_dir():
        for ensemble_path in sorted(ensemble_root.glob("*/ensemble.json")):
            ensemble = _read_json_object(ensemble_path, "ensemble lineage")
            if (
                ensemble.get("task_id") != task_id
                or ensemble.get("dry_run") is not False
                or ensemble.get("complete") is not True
            ):
                continue
            records = ensemble.get("rollouts")
            if not isinstance(records, list):
                continue
            for record in records:
                if not isinstance(record, dict) or record.get("run_dir") != run_relative:
                    continue
                if record.get("status") != "completed":
                    raise RouteError("ensemble lineage does not mark the rollout completed")
                matches.append((ensemble_path, ensemble, record))
    if len(matches) != 1:
        raise RouteError(
            "agent rollout must have exactly one completed non-dry ensemble lineage record; "
            f"found {len(matches)}"
        )

    ensemble_path, ensemble, record = matches[0]
    # Authenticate the *entire* breadth ensemble, not only the card currently
    # being imported. Otherwise one real run plus dummy "completed" siblings
    # could manufacture a full-width lineage record.
    from .protocol import _validated_fanout_result_paths

    validated_results = _validated_fanout_result_paths(root, str(task_id), ensemble_path)
    if validated_results is None:
        raise RouteError("complete ensemble failed atomic rollout validation")
    if (run_dir / "result.json").resolve() not in {
        result_path.resolve() for result_path in validated_results
    }:
        raise RouteError("imported run is not a validated member of the complete ensemble")
    ensemble_rollouts = ensemble.get("rollouts")
    if not isinstance(ensemble_rollouts, list) or any(
        not isinstance(candidate, Mapping) or candidate.get("status") != "completed"
        for candidate in ensemble_rollouts
    ):
        raise RouteError("complete ensemble lineage must mark every rollout completed")
    for field in ("rollout_id", "worker", "method_family"):
        if record.get(field) != strategy[field]:
            raise RouteError(f"ensemble rollout {field} does not match invocation lineage")
    attested_paths = {
        "invocation_sha256": run_dir / "invocation.json",
        "task_sha256": run_dir / "task.json",
        "validation_sha256": run_dir / "validation.json",
        "result_sha256": run_dir / "result.json",
        "artifact_manifest_sha256": run_dir / "artifact_manifest.json",
        "trusted_preflight_sha256": run_dir / "trusted_verifiers.preflight.json",
        "trusted_final_sha256": run_dir / "trusted_verifiers.json",
    }
    expected_attestations = set(attested_paths) | {
        "artifact_tree_sha256",
        "verifier_log_tree_sha256",
    }
    recorded_attestation = record.get("run_attestation")
    if not isinstance(recorded_attestation, Mapping) or set(
        recorded_attestation
    ) != expected_attestations:
        raise RouteError("complete ensemble rollout has a malformed run_attestation")
    mismatched_attestations = [
        name
        for name, path in attested_paths.items()
        if recorded_attestation.get(name) != _sha256_path(path)
    ]
    if mismatched_attestations:
        raise RouteError(
            "complete ensemble rollout run_attestation SHA-256 mismatch: "
            + ", ".join(sorted(mismatched_attestations))
        )

    manifest_path = _recorded_repo_path(
        root, ensemble.get("source_manifest"), "ensemble source_manifest"
    )
    if not manifest_path.is_file():
        raise RouteError("ensemble source manifest is unavailable for lineage verification")
    manifest_hash = ensemble.get("source_manifest_sha256")
    if not isinstance(manifest_hash, str) or _sha256_path(manifest_path) != manifest_hash:
        raise RouteError("ensemble source manifest hash does not match its recorded lineage")
    manifest = _read_json_object(manifest_path, "fanout manifest")
    if manifest.get("task_id") != task_id:
        raise RouteError("fanout manifest task_id does not match the completed run")
    from .fanout import validate_fanout_manifest  # lazy: avoid coupling basic DAG use to fanout

    manifest_errors = validate_fanout_manifest(manifest, task_id=str(task_id))
    if manifest_errors:
        raise RouteError("hashed source fanout manifest is invalid: " + "; ".join(manifest_errors))
    source_rollouts = manifest.get("rollouts")
    if not isinstance(source_rollouts, list):
        raise RouteError("fanout manifest has no rollout list")
    source_matches = [
        rollout
        for rollout in source_rollouts
        if isinstance(rollout, dict) and rollout.get("rollout_id") == strategy["rollout_id"]
    ]
    if len(source_matches) != 1 or source_matches[0] != strategy:
        raise RouteError("invocation rollout_strategy does not exactly match its hashed source manifest")
    if not isinstance(ensemble_rollouts, list) or {
        record.get("rollout_id") for record in ensemble_rollouts if isinstance(record, Mapping)
    } != {
        rollout.get("rollout_id") for rollout in source_rollouts if isinstance(rollout, Mapping)
    }:
        raise RouteError("ensemble records do not cover exactly the hashed manifest rollouts")
    return strategy


def _matching_sealed_result_avenue(
    card: Mapping[str, Any], result: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Return the unique final avenue that reconstructs the locked card."""

    iteration = result.get("iteration")
    avenues = iteration.get("avenues") if isinstance(iteration, Mapping) else None
    if not isinstance(avenues, list):
        raise RouteError("completed sealed result has no iteration.avenues registry")
    matches = [
        avenue
        for avenue in avenues
        if isinstance(avenue, Mapping)
        and all(avenue.get(field) == card.get(field) for field in SEALED_CARD_AVENUE_FIELDS)
    ]
    if len(matches) != 1:
        core_matches = [
            avenue
            for avenue in avenues
            if isinstance(avenue, Mapping)
            and all(
                avenue.get(field) == card.get(field)
                for field in (
                    "method_family",
                    "representation",
                    "state_or_invariant",
                    "core_candidate_lemma",
                )
            )
        ]
        mismatches = sorted(
            {
                field
                for avenue in core_matches
                for field in SEALED_CARD_AVENUE_FIELDS
                if avenue.get(field) != card.get(field)
            }
        )
        detail = f"; locked fields changed: {mismatches}" if mismatches else ""
        raise RouteError(
            "completed sealed result must contain exactly one avenue matching the locked card; "
            f"found {len(matches)}{detail}"
        )
    return matches[0]


def _registry_state_from_avenue(avenue: Mapping[str, Any]) -> tuple[str, str, list[str]]:
    """Map a worker verdict without promoting a blocked card to an active route."""

    status = _normalized_signature_text(avenue.get("status"))
    decision = _normalized_signature_text(avenue.get("decision"))
    if status == "refuted" or decision == "prune":
        # The route generator's own verdict is a valuable obstruction report,
        # but it is not independent E2+ decision evidence.  Preserve and
        # suspend the card until a critic supplies an exact/certified witness.
        return "suspended", "suspend", [INDEPENDENT_REFUTATION_REOPEN]
    if status == "blocked" or decision == "suspend":
        # result.schema.json has no reopen_if field.  Keeping this proposed is
        # safer than inventing a condition on the worker's behalf.
        return "proposed", "unreviewed", []
    if status in {"open", "advanced", "completed"} or decision == "complete":
        # A generator's positive verdict is not an independent target-fidelity
        # review.  Keep the imported avenue outside the active portfolio until
        # a different reviewer checks that it really targets C050 as stated.
        return "proposed", "unreviewed", []
    return "proposed", "unreviewed", []


def import_route_card(root: Path, card_path: Path, route_id: str) -> Path:
    """Import one completed, Agent-generated sealed card as an L1 scout route.

    The source must be exactly ``runs/<task>/<run>/artifacts/route_card.json``.
    Completion, final and sealed-phase validation, both recorded hashes, and
    hashed fanout/ensemble lineage are checked before a new registry file is
    created.  The immutable card is copied into tracked research memory, and a
    blocked or refuted final avenue is never promoted to active/scout.
    """

    root = Path(root).resolve()
    if not isinstance(route_id, str) or not ROUTE_ID_PATTERN.fullmatch(route_id):
        raise RouteError(f"route_id must match {ROUTE_ID_PATTERN.pattern}")
    output = root / "research" / "routes" / f"{route_id}.json"
    existing_routes = load_route_nodes(root)
    if output.exists() or any(route.get("route_id") == route_id for route in existing_routes):
        raise RouteError(f"route registry already contains {route_id}; refusing to overwrite")

    candidate = Path(card_path)
    resolved_card = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        card_relative = resolved_card.relative_to(root)
    except ValueError as error:
        raise RouteError("route card must be inside this repository") from error
    if (
        len(card_relative.parts) != 5
        or card_relative.parts[0] != "runs"
        or card_relative.parts[-2:] != ("artifacts", "route_card.json")
    ):
        raise RouteError(
            "route card must be runs/<task>/<run>/artifacts/route_card.json, not a "
            "coordinator card or arbitrary JSON"
        )
    if not resolved_card.is_file():
        raise RouteError(f"route card does not exist: {resolved_card}")
    run_dir = resolved_card.parent.parent
    task_id = card_relative.parts[1]
    run_id = card_relative.parts[2]

    card = _read_json_object(resolved_card, "route card")
    card_origin = card.get("route_card_origin")
    nested_origin = card.get("provenance")
    if card_origin == "coordinator_precommit" or (
        isinstance(nested_origin, Mapping)
        and nested_origin.get("route_card_origin") == "coordinator_precommit"
    ):
        raise RouteError("coordinator_precommit cards cannot be imported as agent-generated breadth")

    invocation_path = run_dir / "invocation.json"
    task_path = run_dir / "task.json"
    result_path = run_dir / "result.json"
    final_validation_path = run_dir / "validation.json"
    for path, label in (
        (invocation_path, "invocation"),
        (task_path, "recorded task"),
        (result_path, "completed result"),
        (final_validation_path, "final validation"),
    ):
        if not path.is_file():
            raise RouteError(f"completed sealed run is missing {label}: {path}")
    invocation = _read_json_object(invocation_path, "invocation")
    recorded_task = _read_json_object(task_path, "recorded task")
    result = _read_json_object(result_path, "completed result")
    final_validation = _read_json_object(final_validation_path, "final validation")
    if invocation.get("task_id") != task_id or invocation.get("run_id") != run_id:
        raise RouteError("card path task/run identity does not match invocation")
    if recorded_task.get("task_id") != task_id or result.get("task_id") != task_id:
        raise RouteError("recorded task/result lineage does not match the card task")
    if result.get("run_id") != run_id or result.get("worker") != invocation.get("worker"):
        raise RouteError("completed result run/worker identity does not match invocation lineage")
    if _is_checkpoint_resume(invocation):
        raise RouteError(
            "checkpoint-resumed runs cannot be imported as independent sealed breadth"
        )
    if invocation.get("dry_run") is not False:
        raise RouteError("dry-run cards cannot enter the route registry")
    if invocation.get("iteration_complete") is not True or invocation.get("exit_code") != 0:
        raise RouteError("route card run is not marked successfully completed")
    _validated_active_research_time(root, invocation)
    if invocation.get("research_mode") != "sealed_breadth":
        raise RouteError("route card did not come from a sealed_breadth run")
    if invocation.get("context_policy", {}).get("mode") != "statement_only":
        raise RouteError("route card invocation was not statement-only")
    if recorded_task.get("fanout_manifest") is not None and invocation.get(
        "rollout_strategy"
    ) is None:
        raise RouteError(
            "task declares an official fanout_manifest; a standalone sealed run "
            "cannot be imported as independent breadth"
        )
    if final_validation.get("valid") is not True or final_validation.get("errors") not in (
        [],
        None,
    ):
        raise RouteError("completed sealed run final validation.valid is not true")

    recorded_card = invocation.get("route_card")
    if not isinstance(recorded_card, Mapping):
        raise RouteError("invocation is missing its locked route_card record")
    recorded_card_path = _recorded_repo_path(
        root, recorded_card.get("path"), "invocation route_card.path"
    )
    if recorded_card_path != resolved_card:
        raise RouteError("requested card is not the route card locked by the invocation")
    current_hash = _sha256_path(resolved_card)
    if recorded_card.get("sha256") != current_hash or invocation.get("route_card_sha256") != current_hash:
        raise RouteError("current route card SHA-256 does not match the completed invocation")

    phases = invocation.get("phases")
    sealed_phases = (
        [phase for phase in phases if isinstance(phase, Mapping) and phase.get("phase_kind") == "sealed_route_card"]
        if isinstance(phases, list)
        else []
    )
    if len(sealed_phases) != 1:
        raise RouteError("completed invocation must identify exactly one sealed route-card phase")
    phase_result_raw = sealed_phases[0].get("result")
    phase_result = _recorded_repo_path(root, phase_result_raw, "sealed phase result")
    if phase_result.parent != run_dir:
        raise RouteError("sealed phase result is outside its run directory")
    if not phase_result.is_file():
        raise RouteError("sealed phase result recorded by the invocation is missing")
    if _sha256_path(phase_result) != current_hash:
        raise RouteError("sealed phase structured card does not match the durable route card")
    match = re.fullmatch(r"(phase-[0-9]{3})-result\.json", phase_result.name)
    if match is None:
        raise RouteError("sealed phase result has an unrecognized name")
    validation_path = run_dir / f"{match.group(1)}-validation.json"
    if not validation_path.is_file():
        raise RouteError("sealed route-card phase has no validation record")
    validation = _read_json_object(validation_path, "sealed phase validation")
    if validation.get("valid") is not True or validation.get("errors") not in ([], None):
        raise RouteError("sealed route-card phase validation.valid is not true")

    strategy = _verified_rollout_strategy(root, run_dir, invocation)
    from .protocol import validate_route_card  # lazy: preserve standalone route-DAG use

    card_errors = validate_route_card(card, task=recorded_task, rollout_strategy=strategy)
    if card_errors:
        raise RouteError("route card no longer validates: " + "; ".join(card_errors))
    if card.get("context_mode") != "statement_only":
        raise RouteError("only a statement-only card may be registered as sealed breadth")
    matching_avenue = _matching_sealed_result_avenue(card, result)
    route_status, route_decision, reopen_if = _registry_state_from_avenue(matching_avenue)

    routes_by_id = {route.get("route_id"): route for route in existing_routes}
    parent_ids = card.get("parent_route_ids")
    if not isinstance(parent_ids, list) or not parent_ids:
        raise RouteError("an imported L1 route requires at least one L0 parent")
    missing_parents = [parent_id for parent_id in parent_ids if parent_id not in routes_by_id]
    if missing_parents:
        raise RouteError(f"route card refers to unknown parent routes {missing_parents}")
    non_root_parents = [
        parent_id for parent_id in parent_ids if routes_by_id[parent_id].get("layer") != "L0"
    ]
    if non_root_parents:
        raise RouteError(f"imported L1 route parents must be L0 nodes: {non_root_parents}")
    target_claims = {routes_by_id[parent_id].get("target_claim_id") for parent_id in parent_ids}
    if len(target_claims) != 1 or not _is_nonempty_string(next(iter(target_claims), None)):
        raise RouteError("L0 parents do not identify one unambiguous target claim")
    target_claim_id = next(iter(target_claims))

    tracked_card = root / "research" / "routes" / "cards" / f"{route_id}.json"
    if tracked_card.exists():
        raise RouteError(f"tracked route-card memory already contains {route_id}; refusing to overwrite")
    tracked_relative = tracked_card.relative_to(root).as_posix()

    route = {
        "schema_version": "1.0",
        "route_id": route_id,
        "layer": "L1",
        "title": f"Agent-generated sealed route: {card['route_card_id']}",
        "statement": card["core_candidate_lemma"],
        "parent_ids": list(parent_ids),
        "method_family": card["method_family"],
        "target_claim_id": target_claim_id,
        "signature": {
            "representation": card["representation"],
            "state_or_invariant": card["state_or_invariant"],
            "core_candidate_lemma": card["core_candidate_lemma"],
            "information_retained": list(card["information_retained"]),
            "information_discarded": list(card["information_discarded"]),
            "target_implication": card["target_implication"],
            "known_failure_mode": card["predicted_failure"],
            "verifier_class": f"Agent-declared first falsifier: {card['falsifier']}",
        },
        "status": route_status,
        "decision": route_decision,
        "merge_target_id": None,
        "reopen_if": reopen_if,
        "score": {
            "target_transfer": 1,
            "counterexample_resistance": 1,
            "blocker_specificity": 2,
            "falsifiability": 2,
            "recent_information_gain": 0,
        },
        "provenance": {
            "search_mode": "sealed_breadth",
            "initial_context": "statement_only",
            "route_card_hash": current_hash,
            "route_card_origin": "agent_generated",
            "agent_rollout_id": card["rollout_id"],
            "agent_worker": invocation["worker"],
            "agent_run_id": run_id,
            "source_card_path": tracked_relative,
            "independent_breadth_eligible": True,
            "resumed_from_checkpoint": False,
        },
    }
    route_errors = validate_route_dag([*existing_routes, route])
    if route_errors:
        raise RouteError("imported route would invalidate the route DAG: " + "; ".join(route_errors))

    output.parent.mkdir(parents=True, exist_ok=True)
    tracked_card.parent.mkdir(parents=True, exist_ok=True)
    try:
        card_bytes = resolved_card.read_bytes()
    except OSError as error:
        raise RouteError(f"cannot copy immutable route card {resolved_card}: {error}") from error
    tracked_created = False
    output_created = False
    try:
        with tracked_card.open("xb") as handle:
            tracked_created = True
            handle.write(card_bytes)
        with output.open("x", encoding="utf-8") as handle:
            output_created = True
            json.dump(route, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except FileExistsError as error:
        if tracked_created:
            tracked_card.unlink(missing_ok=True)
        raise RouteError(f"route registry already contains {route_id}; refusing to overwrite") from error
    except OSError as error:
        if output_created:
            output.unlink(missing_ok=True)
        if tracked_created:
            tracked_card.unlink(missing_ok=True)
        raise RouteError(f"cannot write imported route {route_id}: {error}") from error
    return output


def review_route_target(root: Path, route_id: str, review_path: Path) -> Path:
    """Apply an independent target-fidelity review to one proposed route.

    Importing a generator's card records a candidate, not an active avenue.
    This transition binds a different review worker to the exact pre-review
    route and immutable card hashes.  It is a process gate only: activation as
    a scout is not mathematical evidence for the route's lemma.
    """

    root = Path(root).resolve()
    if not isinstance(route_id, str) or not ROUTE_ID_PATTERN.fullmatch(route_id):
        raise RouteError(f"route_id must match {ROUTE_ID_PATTERN.pattern}")
    route_file = root / "research" / "routes" / f"{route_id}.json"
    if not route_file.is_file():
        raise RouteError(f"unknown route id: {route_id}")
    route = _read_json_object(route_file, "route node")
    if route.get("route_id") != route_id:
        raise RouteError("route filename and route_id disagree")
    if (route.get("status"), route.get("decision")) != ("proposed", "unreviewed"):
        raise RouteError("only a proposed/unreviewed route may pass target review")
    existing_provenance = route.get("provenance")
    if not isinstance(existing_provenance, Mapping) or not (
        existing_provenance.get("route_card_origin") == "agent_generated"
        or existing_provenance.get("source_result_path") is not None
    ):
        raise RouteError("controlled target review is only for an Agent-created route")

    candidate = Path(review_path)
    resolved_review = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        resolved_review.relative_to(root)
    except ValueError as error:
        raise RouteError("route review must be inside this repository") from error
    if not resolved_review.is_file():
        raise RouteError(f"route review does not exist: {resolved_review}")
    review = _read_json_object(resolved_review, "route target review")
    required = {
        "schema_version",
        "kind",
        "review_id",
        "route_id",
        "reviewer_task_id",
        "reviewer_worker",
        "reviewer_run_id",
        "source_route_sha256",
        "route_card_sha256",
        "target_claim_id",
        "decision",
        "checks",
        "rationale",
        "evidence_artifacts",
        "reopen_if",
    }
    missing = sorted(required - set(review))
    extra = sorted(set(review) - required)
    if missing or extra:
        raise RouteError(
            f"route target review fields invalid; missing={missing}, unsupported={extra}"
        )
    if review.get("schema_version") != "1.0" or review.get("kind") != "rpcd-route-target-review":
        raise RouteError("unsupported route target review kind or schema version")
    for field in (
        "review_id",
        "reviewer_task_id",
        "reviewer_worker",
        "reviewer_run_id",
        "rationale",
    ):
        if not _is_nonempty_string(review.get(field)):
            raise RouteError(f"route target review {field} must be a nonempty string")
    if review.get("route_id") != route_id:
        raise RouteError("route target review route_id does not match the selected route")
    if review.get("target_claim_id") != route.get("target_claim_id"):
        raise RouteError("route target review target_claim_id does not match the route")
    source_hash = _sha256_path(route_file)
    if review.get("source_route_sha256") != source_hash:
        raise RouteError("route target review does not bind the current pre-review route SHA-256")
    provenance = route.get("provenance")
    if not isinstance(provenance, dict):
        raise RouteError("route has malformed provenance")
    card_hash = provenance.get("route_card_hash")
    if review.get("route_card_sha256") != card_hash:
        raise RouteError("route target review does not bind the immutable route-card SHA-256")
    generator_worker = provenance.get("agent_worker")
    if _is_nonempty_string(generator_worker) and review["reviewer_worker"] == generator_worker:
        raise RouteError("route target reviewer must be independent of the generating worker")
    reviewer_artifact_dir, reviewer_run_attestation = _validated_standalone_reviewer_run(
        root,
        review,
        resolved_review,
        label="route target reviewer",
    )

    checks = review.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != set(TARGET_REVIEW_CHECKS):
        raise RouteError(
            "route target review checks must be exactly: " + ", ".join(TARGET_REVIEW_CHECKS)
        )
    if any(not isinstance(checks[field], bool) for field in TARGET_REVIEW_CHECKS):
        raise RouteError("every route target review check must be boolean")
    decision = review.get("decision")
    if decision not in {"activate_scout", "suspend"}:
        raise RouteError("route target review decision must be activate_scout or suspend")
    if decision == "activate_scout" and any(checks[field] is not True for field in TARGET_REVIEW_CHECKS):
        raise RouteError("activate_scout requires every RPCD target-fidelity check to be true")
    evidence = review.get("evidence_artifacts")
    evidence_errors = _string_list_errors(evidence, "route target review evidence_artifacts")
    if evidence_errors or not evidence:
        raise RouteError(
            "route target review evidence_artifacts must be a nonempty unique string array"
        )
    for raw in evidence:
        artifact = _recorded_repo_path(root, raw, "route target review evidence artifact")
        if not artifact.is_file():
            raise RouteError(f"route target review evidence artifact is missing: {raw}")
        try:
            artifact.relative_to(reviewer_artifact_dir)
        except ValueError as error:
            raise RouteError(
                "route target review evidence artifact does not belong to the reviewer harness run"
            ) from error
    reopen_if = review.get("reopen_if")
    reopen_errors = _string_list_errors(reopen_if, "route target review reopen_if")
    if reopen_errors:
        raise RouteError("; ".join(reopen_errors))
    if decision == "activate_scout" and reopen_if:
        raise RouteError("activate_scout review must have an empty reopen_if")
    if decision == "suspend" and not reopen_if:
        raise RouteError("suspend review requires a nonempty reopen_if")

    tracked_review = root / "research" / "routes" / "reviews" / f"{route_id}.json"
    if tracked_review.exists():
        raise RouteError(f"tracked route review already contains {route_id}; refusing to overwrite")
    review_hash = _sha256_path(resolved_review)
    provenance.update(
        source_review_path=tracked_review.relative_to(root).as_posix(),
        route_review_hash=review_hash,
        reviewer_task_id=review["reviewer_task_id"],
        reviewer_worker=review["reviewer_worker"],
        reviewer_run_id=review["reviewer_run_id"],
        reviewer_run_attestation=reviewer_run_attestation,
    )
    if decision == "activate_scout":
        route.update(status="active", decision="scout", reopen_if=[])
    else:
        route.update(status="suspended", decision="suspend", reopen_if=list(reopen_if))

    prospective = [
        route if candidate_route.get("route_id") == route_id else candidate_route
        for candidate_route in load_route_nodes(root)
    ]
    errors = validate_route_dag(prospective)
    if errors:
        raise RouteError("review transition would invalidate the route DAG: " + "; ".join(errors))

    tracked_review.parent.mkdir(parents=True, exist_ok=True)
    review_bytes = resolved_review.read_bytes()
    temporary_route = route_file.with_name(route_file.name + ".review-tmp")
    tracked_created = False
    try:
        with tracked_review.open("xb") as handle:
            tracked_created = True
            handle.write(review_bytes)
        with temporary_route.open("x", encoding="utf-8") as handle:
            json.dump(route, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_route.replace(route_file)
    except OSError as error:
        temporary_route.unlink(missing_ok=True)
        if tracked_created:
            tracked_review.unlink(missing_ok=True)
        raise RouteError(f"cannot apply route target review for {route_id}: {error}") from error
    return route_file


def _validated_standalone_reviewer_run(
    root: Path,
    record: Mapping[str, Any],
    resolved_record: Path,
    *,
    label: str,
) -> tuple[Path, dict[str, str]]:
    """Bind a reviewer record to one canonical completed standalone harness run."""

    task_id = record.get("reviewer_task_id")
    run_id = record.get("reviewer_run_id")
    if not _is_nonempty_string(task_id) or not _is_nonempty_string(run_id):
        raise RouteError(f"{label} task/run identity must be nonempty")
    run_dir = _recorded_repo_path(
        root,
        f"runs/{task_id}/{run_id}",
        f"{label} run",
    )
    try:
        relative_run = run_dir.relative_to(root)
    except ValueError as error:  # defensive: _recorded_repo_path already checks this
        raise RouteError(f"{label} run escapes the repository") from error
    if (
        len(relative_run.parts) != 3
        or relative_run.parts[0] != "runs"
        or relative_run.parts[1] != task_id
        or relative_run.parts[2] != run_id
    ):
        raise RouteError(f"{label} run must be runs/<task>/<run>")
    artifact_dir = (run_dir / "artifacts").resolve()
    try:
        resolved_record.relative_to(artifact_dir)
    except ValueError as error:
        raise RouteError(
            f"{label} record must be an artifact of its reviewer harness run"
        ) from error

    invocation_path = run_dir / "invocation.json"
    if not invocation_path.is_file():
        raise RouteError(f"{label} run has no invocation.json")
    invocation = _read_json_object(invocation_path, f"{label} invocation")
    if invocation.get("rollout_strategy") is not None:
        raise RouteError(f"{label} must use a standalone harness run")
    if invocation.get("worker") != record.get("reviewer_worker"):
        raise RouteError(f"{label} reviewer_worker does not match its harness invocation")

    from .fanout import _validated_run_attestation
    from .protocol import ProtocolError

    try:
        canonical_run, attestation = _validated_run_attestation(
            root,
            str(task_id),
            None,
            run_dir,
        )
    except (OSError, ProtocolError, ValueError) as error:
        raise RouteError(
            f"{label} run is not a canonical completed validated 120-minute run: "
            f"{error}"
        ) from error
    if canonical_run != relative_run.as_posix():
        raise RouteError(f"{label} run path is not canonical")
    if set(attestation) != RUN_ATTESTATION_FIELDS or any(
        not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest)
        for digest in attestation.values()
    ):
        raise RouteError(f"{label} run returned malformed canonical attestation")
    return artifact_dir, attestation


def prune_route(root: Path, route_id: str, verdict_path: Path) -> Path:
    """Hard-prune one route only from an independent E2+ exact certificate.

    This transition concerns the route-local lemma only.  The minimal command
    intentionally has no authority to mark C050 (or another master claim)
    refuted; such a claim requires a separate, explicitly authorized ledger
    workflow over the full canonical negation.
    """

    root = Path(root).resolve()
    if not isinstance(route_id, str) or not ROUTE_ID_PATTERN.fullmatch(route_id):
        raise RouteError(f"route_id must match {ROUTE_ID_PATTERN.pattern}")
    route_file = root / "research" / "routes" / f"{route_id}.json"
    if not route_file.is_file():
        raise RouteError(f"unknown route id: {route_id}")
    route = _read_json_object(route_file, "route node")
    if route.get("route_id") != route_id:
        raise RouteError("route filename and route_id disagree")
    if route.get("status") not in {"proposed", "active", "suspended"}:
        raise RouteError("only a proposed, active, or suspended route may be hard-pruned")
    live_children = [
        candidate_route.get("route_id")
        for candidate_route in load_route_nodes(root)
        if route_id in candidate_route.get("parent_ids", [])
        and candidate_route.get("status") in {"proposed", "active", "completed"}
    ]
    if live_children:
        raise RouteError(
            "cannot hard-prune a route with live dependent children; suspend or resolve them "
            f"first: {sorted(str(child) for child in live_children)}"
        )

    candidate = Path(verdict_path)
    resolved_verdict = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        resolved_verdict.relative_to(root)
    except ValueError as error:
        raise RouteError("route prune verdict must be inside this repository") from error
    if not resolved_verdict.is_file():
        raise RouteError(f"route prune verdict does not exist: {resolved_verdict}")
    verdict = _read_json_object(resolved_verdict, "route prune verdict")
    required = {
        "schema_version",
        "kind",
        "verdict_id",
        "route_id",
        "reviewer_task_id",
        "reviewer_worker",
        "reviewer_run_id",
        "source_route_sha256",
        "route_card_sha256",
        "target_claim_id",
        "route_local_statement",
        "evidence_level",
        "certificate_kind",
        "certificate_artifacts",
        "master_claim_affected",
        "rationale",
    }
    missing = sorted(required - set(verdict))
    extra = sorted(set(verdict) - required)
    if missing or extra:
        raise RouteError(
            f"route prune verdict fields invalid; missing={missing}, unsupported={extra}"
        )
    if verdict.get("schema_version") != "1.0" or verdict.get("kind") != "rpcd-route-prune-verdict":
        raise RouteError("unsupported route prune verdict kind or schema version")
    for field in (
        "verdict_id",
        "reviewer_task_id",
        "reviewer_worker",
        "reviewer_run_id",
        "rationale",
    ):
        if not _is_nonempty_string(verdict.get(field)):
            raise RouteError(f"route prune verdict {field} must be a nonempty string")
    if verdict.get("route_id") != route_id:
        raise RouteError("route prune verdict route_id does not match the selected route")
    if verdict.get("target_claim_id") != route.get("target_claim_id"):
        raise RouteError("route prune verdict target_claim_id does not match the route")
    if verdict.get("route_local_statement") != route.get("statement"):
        raise RouteError("route prune verdict does not bind the exact route-local statement")
    if verdict.get("master_claim_affected") is not False:
        raise RouteError(
            "the route-prune transition requires master_claim_affected=false; "
            "it cannot refute C050 or another master claim"
        )
    if verdict.get("evidence_level") not in PRUNE_EVIDENCE_LEVELS:
        raise RouteError("route hard-prune requires evidence_level E2 or higher")
    if verdict.get("certificate_kind") not in PRUNE_CERTIFICATE_KINDS:
        raise RouteError(
            "route hard-prune requires an exact_counterexample or certified_counterexample"
        )
    if verdict.get("source_route_sha256") != _sha256_path(route_file):
        raise RouteError("route prune verdict does not bind the current source route SHA-256")
    provenance = route.get("provenance")
    if not isinstance(provenance, dict):
        raise RouteError("route has malformed provenance")
    if verdict.get("route_card_sha256") != provenance.get("route_card_hash"):
        raise RouteError("route prune verdict does not bind the route-card SHA-256")
    generator_worker = provenance.get("agent_worker")
    if _is_nonempty_string(generator_worker) and verdict["reviewer_worker"] == generator_worker:
        raise RouteError("route prune reviewer must be independent of the generating worker")
    reviewer_artifact_dir, reviewer_run_attestation = _validated_standalone_reviewer_run(
        root,
        verdict,
        resolved_verdict,
        label="route prune reviewer",
    )
    artifacts = verdict.get("certificate_artifacts")
    artifact_errors = _string_list_errors(
        artifacts, "route prune verdict certificate_artifacts"
    )
    if artifact_errors or not artifacts:
        raise RouteError("route hard-prune requires nonempty unique certificate_artifacts")
    certificate_copies: list[tuple[Path, Path, str]] = []
    tracked_certificate_dir = root / "research" / "routes" / "certificates" / route_id
    for index, raw in enumerate(artifacts):
        artifact = _recorded_repo_path(root, raw, "route prune certificate artifact")
        if not artifact.is_file():
            raise RouteError(f"route prune certificate artifact is missing: {raw}")
        try:
            artifact.relative_to(reviewer_artifact_dir)
        except ValueError as error:
            raise RouteError(
                "route prune certificate artifact does not belong to the reviewer harness run"
            ) from error
        tracked_artifact = tracked_certificate_dir / f"{index:03d}-{artifact.name}"
        if tracked_artifact.exists():
            raise RouteError(
                f"tracked prune certificate already exists: {tracked_artifact.relative_to(root)}"
            )
        certificate_copies.append((artifact, tracked_artifact, _sha256_path(artifact)))

    tracked_verdict = root / "research" / "routes" / "verdicts" / f"{route_id}.json"
    if tracked_verdict.exists():
        raise RouteError(f"tracked prune verdict already contains {route_id}; refusing to overwrite")
    verdict_hash = _sha256_path(resolved_verdict)
    provenance.update(
        source_prune_path=tracked_verdict.relative_to(root).as_posix(),
        route_prune_hash=verdict_hash,
        prune_reviewer_task_id=verdict["reviewer_task_id"],
        prune_reviewer_worker=verdict["reviewer_worker"],
        prune_reviewer_run_id=verdict["reviewer_run_id"],
        prune_reviewer_run_attestation=reviewer_run_attestation,
        prune_evidence_level=verdict["evidence_level"],
        prune_certificate_kind=verdict["certificate_kind"],
        prune_certificate_artifacts=[
            {
                "path": tracked.relative_to(root).as_posix(),
                "sha256": digest,
            }
            for _, tracked, digest in certificate_copies
        ],
    )
    route.update(status="refuted", decision="hard_prune", merge_target_id=None, reopen_if=[])
    prospective = [
        route if candidate_route.get("route_id") == route_id else candidate_route
        for candidate_route in load_route_nodes(root)
    ]
    errors = validate_route_dag(prospective)
    if errors:
        raise RouteError("prune transition would invalidate the route DAG: " + "; ".join(errors))

    tracked_verdict.parent.mkdir(parents=True, exist_ok=True)
    tracked_certificate_dir.mkdir(parents=True, exist_ok=True)
    verdict_bytes = resolved_verdict.read_bytes()
    temporary_route = route_file.with_name(route_file.name + ".prune-tmp")
    tracked_created = False
    certificate_created: list[Path] = []
    try:
        for source, tracked, _ in certificate_copies:
            with tracked.open("xb") as handle:
                handle.write(source.read_bytes())
            certificate_created.append(tracked)
        with tracked_verdict.open("xb") as handle:
            tracked_created = True
            handle.write(verdict_bytes)
        with temporary_route.open("x", encoding="utf-8") as handle:
            json.dump(route, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary_route.replace(route_file)
    except OSError as error:
        temporary_route.unlink(missing_ok=True)
        if tracked_created:
            tracked_verdict.unlink(missing_ok=True)
        for tracked in certificate_created:
            tracked.unlink(missing_ok=True)
        raise RouteError(f"cannot apply route prune verdict for {route_id}: {error}") from error
    return route_file


def validate_continuation_avenue(
    routes: Sequence[Mapping[str, Any]],
    assigned_route_id: str,
    avenue: Mapping[str, Any],
) -> list[str]:
    """Validate that a depth child branches from the exact current frontier edge."""

    errors: list[str] = []
    nodes = {
        str(route.get("route_id")): route
        for route in routes
        if isinstance(route.get("route_id"), str)
    }
    parent = nodes.get(assigned_route_id)
    if parent is None:
        return [f"assigned continuation route is unknown: {assigned_route_id}"]
    frontier_ids = {
        str(route.get("route_id")) for route in active_frontier_routes(routes)
    }
    if assigned_route_id not in frontier_ids:
        errors.append(
            f"assigned continuation route {assigned_route_id} is not a current active frontier node"
        )
    missing = [field for field in CONTINUATION_AVENUE_FIELDS if field not in avenue]
    if missing:
        errors.append(f"continuation avenue missing fields: {sorted(missing)}")
        return errors
    for field in (
        "route_id",
        "method_family",
        "representation",
        "state_or_invariant",
        "core_candidate_lemma",
        "target_implication",
        "predicted_failure",
        "falsifier",
        "first_bad_edge",
        "branch_kind",
        "decision",
    ):
        if not _is_nonempty_string(avenue.get(field)):
            errors.append(f"continuation avenue {field} must be a nonempty string")
    for field in ("parent_route_ids", "information_retained", "information_discarded"):
        errors.extend(_string_list_errors(avenue.get(field), f"continuation avenue {field}"))
        if field != "parent_route_ids" and isinstance(avenue.get(field), list) and not avenue[field]:
            errors.append(f"continuation avenue {field} must not be empty")
    if avenue.get("parent_route_ids") != [assigned_route_id]:
        errors.append(
            "continuation avenue parent_route_ids must be the exact one-element assigned frontier parent"
        )
    expected_source = parent.get("layer")
    if avenue.get("source_layer") != expected_source:
        errors.append(
            f"continuation avenue source_layer must equal parent layer {expected_source!r}"
        )
    source_index = LAYER_INDEX.get(str(expected_source))
    expected_next = (
        LAYERS[source_index + 1]
        if source_index is not None and source_index + 1 < len(LAYERS)
        else None
    )
    if expected_next is None:
        errors.append("an L4 route cannot have an adjacent continuation child")
    elif avenue.get("next_layer") != expected_next:
        errors.append(
            f"continuation avenue next_layer must be the adjacent layer {expected_next!r}"
        )
    new_route_id = avenue.get("route_id")
    if not isinstance(new_route_id, str) or not ROUTE_ID_PATTERN.fullmatch(new_route_id):
        errors.append(f"continuation avenue route_id must match {ROUTE_ID_PATTERN.pattern}")
    elif new_route_id == assigned_route_id or new_route_id in nodes:
        errors.append("continuation avenue route_id must be a fresh child id")
    if avenue.get("branch_kind") not in {"repair", "attack", "depth", "audit"}:
        errors.append("continuation avenue branch_kind is invalid")
    if avenue.get("decision") not in {
        "advance",
        "branch",
        "deepen",
        "prune",
        "suspend",
        "merge",
        "complete",
    }:
        errors.append("continuation avenue decision is invalid")
    return errors


def import_continuation_result(
    root: Path, result_path: Path, *, avenue_index: int = 0
) -> Path:
    """Import one validated continuation avenue as a proposed adjacent child.

    The worker cannot activate, prune, or merge its own child.  A positive child
    enters ``proposed/unreviewed`` and must pass ``review_route_target``; a
    self-reported exact refutation is conservatively suspended pending a critic.
    """

    root = Path(root).resolve()
    candidate = Path(result_path)
    resolved_result = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        relative = resolved_result.relative_to(root)
    except ValueError as error:
        raise RouteError("continuation result must be inside this repository") from error
    if (
        len(relative.parts) != 4
        or relative.parts[0] != "runs"
        or relative.parts[-1] != "result.json"
    ):
        raise RouteError("continuation result must be runs/<task>/<run>/result.json")
    if not resolved_result.is_file():
        raise RouteError(f"continuation result does not exist: {resolved_result}")
    task_id, run_id = relative.parts[1], relative.parts[2]
    run_dir = resolved_result.parent
    invocation_path = run_dir / "invocation.json"
    task_path = run_dir / "task.json"
    validation_path = run_dir / "validation.json"
    for path, label in (
        (invocation_path, "invocation"),
        (task_path, "recorded task"),
        (validation_path, "final validation"),
    ):
        if not path.is_file():
            raise RouteError(f"continuation run is missing {label}: {path}")
    invocation = _read_json_object(invocation_path, "continuation invocation")
    task = _read_json_object(task_path, "recorded continuation task")
    result = _read_json_object(resolved_result, "completed continuation result")
    validation = _read_json_object(validation_path, "continuation final validation")
    if task.get("task_id") != task_id or result.get("task_id") != task_id:
        raise RouteError("continuation task/result identity does not match its run path")
    if invocation.get("task_id") != task_id or invocation.get("run_id") != run_id:
        raise RouteError("continuation invocation identity does not match its run path")
    if result.get("run_id") != run_id or result.get("worker") != invocation.get("worker"):
        raise RouteError("continuation result run/worker identity does not match invocation")
    resumed_from_checkpoint = _is_checkpoint_resume(invocation)
    if task.get("research_mode") != "continuation_depth" or invocation.get(
        "research_mode"
    ) != "continuation_depth":
        raise RouteError("controlled depth import requires a continuation_depth task and run")
    if invocation.get("dry_run") is not False:
        raise RouteError("dry-run continuation results cannot enter the route registry")
    if invocation.get("iteration_complete") is not True or invocation.get("exit_code") != 0:
        raise RouteError("continuation run is not marked successfully completed")
    _validated_active_research_time(root, invocation)
    if validation.get("valid") is not True or validation.get("errors") not in ([], None):
        raise RouteError("continuation final validation.valid is not true")
    assigned = task.get("route_ids")
    if not isinstance(assigned, list) or len(assigned) != 1 or not _is_nonempty_string(assigned[0]):
        raise RouteError("continuation task must assign exactly one route_id")

    from .protocol import validate_result  # lazy: keep standalone DAG loading light

    result_errors = validate_result(
        result,
        task=task,
        active_seconds=invocation.get("active_research_seconds"),
        rollout_strategy=invocation.get("rollout_strategy"),
        root=root,
    )
    if result_errors:
        raise RouteError("continuation result no longer validates: " + "; ".join(result_errors))
    avenues = result.get("iteration", {}).get("avenues")
    if not isinstance(avenues, list) or not isinstance(avenue_index, int) or isinstance(
        avenue_index, bool
    ):
        raise RouteError("continuation avenue_index must select an avenue array entry")
    if not 0 <= avenue_index < len(avenues) or not isinstance(avenues[avenue_index], Mapping):
        raise RouteError("continuation avenue_index is out of range or not an object")
    avenue = avenues[avenue_index]
    selected_route_id = avenue.get("route_id")
    if sum(
        1
        for candidate_avenue in avenues
        if isinstance(candidate_avenue, Mapping)
        and candidate_avenue.get("route_id") == selected_route_id
    ) != 1:
        raise RouteError("continuation result must name the selected child route_id exactly once")
    routes = load_route_nodes(root)
    avenue_errors = validate_continuation_avenue(routes, assigned[0], avenue)
    if avenue_errors:
        raise RouteError("invalid continuation transition: " + "; ".join(avenue_errors))

    route_id = str(avenue["route_id"])
    output = root / "research" / "routes" / f"{route_id}.json"
    tracked_result = root / "research" / "routes" / "results" / f"{route_id}.json"
    if output.exists() or tracked_result.exists():
        raise RouteError(f"route registry already contains {route_id}; refusing to overwrite")
    parent = next(route for route in routes if route.get("route_id") == assigned[0])
    status, decision, reopen_if = _registry_state_from_avenue(avenue)
    if status not in {"suspended", "proposed"}:
        status, decision, reopen_if = "proposed", "unreviewed", []
    result_hash = _sha256_path(resolved_result)
    route = {
        "schema_version": "1.0",
        "route_id": route_id,
        "layer": avenue["next_layer"],
        "title": f"Agent-generated continuation: {avenue.get('name', route_id)}",
        "statement": avenue["core_candidate_lemma"],
        "parent_ids": [assigned[0]],
        "method_family": avenue["method_family"],
        "target_claim_id": parent["target_claim_id"],
        "signature": {
            "representation": avenue["representation"],
            "state_or_invariant": avenue["state_or_invariant"],
            "core_candidate_lemma": avenue["core_candidate_lemma"],
            "information_retained": list(avenue["information_retained"]),
            "information_discarded": list(avenue["information_discarded"]),
            "target_implication": avenue["target_implication"],
            "known_failure_mode": avenue["predicted_failure"],
            "verifier_class": f"Agent-declared first falsifier: {avenue['falsifier']}",
        },
        "status": status,
        "decision": decision,
        "merge_target_id": None,
        "reopen_if": reopen_if,
        "score": {
            "target_transfer": 1,
            "counterexample_resistance": 1,
            "blocker_specificity": 2,
            "falsifiability": 2,
            "recent_information_gain": 0,
        },
        "provenance": {
            "search_mode": "inherited_depth",
            "initial_context": "continuation",
            "route_card_hash": None,
            "agent_worker": invocation["worker"],
            "agent_run_id": run_id,
            "source_result_path": tracked_result.relative_to(root).as_posix(),
            "source_result_hash": result_hash,
            # A continuation is depth on its parent's branch, never another
            # independent sealed sample.  This remains false whether the
            # process is fresh or resumed on another account.
            "independent_breadth_eligible": False,
            "resumed_from_checkpoint": resumed_from_checkpoint,
        },
    }
    errors = validate_route_dag([*routes, route])
    if errors:
        raise RouteError("continuation child would invalidate the route DAG: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    tracked_result.parent.mkdir(parents=True, exist_ok=True)
    result_bytes = resolved_result.read_bytes()
    tracked_created = False
    output_created = False
    try:
        with tracked_result.open("xb") as handle:
            tracked_created = True
            handle.write(result_bytes)
        with output.open("x", encoding="utf-8") as handle:
            output_created = True
            json.dump(route, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    except OSError as error:
        if output_created:
            output.unlink(missing_ok=True)
        if tracked_created:
            tracked_result.unlink(missing_ok=True)
        raise RouteError(f"cannot import continuation route {route_id}: {error}") from error
    return output


def validate_route_node(route: Mapping[str, Any]) -> list[str]:
    """Validate one route independently of its parents and merge target."""

    route_id = route.get("route_id", "<unknown>")
    prefix = str(route_id)
    required = {
        "schema_version",
        "route_id",
        "layer",
        "title",
        "statement",
        "parent_ids",
        "method_family",
        "target_claim_id",
        "signature",
        "status",
        "decision",
        "merge_target_id",
        "reopen_if",
        "score",
        "provenance",
    }
    missing = required - route.keys()
    if missing:
        return [f"{prefix}: missing route fields {sorted(missing)}"]

    errors: list[str] = []
    if route.get("schema_version") != "1.0":
        errors.append(f"{prefix}: unsupported route schema version")
    if not isinstance(route_id, str) or not ROUTE_ID_PATTERN.fullmatch(route_id):
        errors.append(f"{prefix}: route_id must match {ROUTE_ID_PATTERN.pattern}")
    layer = route.get("layer")
    if layer not in LAYER_INDEX:
        errors.append(f"{prefix}: unknown route layer {layer!r}")
    for field in ("title", "statement", "method_family", "target_claim_id"):
        if not _is_nonempty_string(route.get(field)):
            errors.append(f"{prefix}: {field} must be a nonempty string")
    errors.extend(f"{prefix}: {error}" for error in _string_list_errors(route.get("parent_ids"), "parent_ids"))

    signature = route.get("signature")
    if not isinstance(signature, Mapping):
        errors.append(f"{prefix}: signature must be an object")
    else:
        missing_signature = set(SIGNATURE_FIELDS) - signature.keys()
        if missing_signature:
            errors.append(f"{prefix}: signature missing fields {sorted(missing_signature)}")
        for field in SIGNATURE_FIELDS:
            if field not in signature:
                continue
            if field in SIGNATURE_LIST_FIELDS:
                errors.extend(
                    f"{prefix}: {error}"
                    for error in _string_list_errors(signature[field], f"signature.{field}")
                )
            elif not _is_nonempty_string(signature[field]):
                errors.append(f"{prefix}: signature.{field} must be a nonempty string")

    status = route.get("status")
    decision = route.get("decision")
    if status not in ROUTE_STATUSES:
        errors.append(f"{prefix}: unknown route status {status!r}")
    if decision not in ROUTE_DECISIONS:
        errors.append(f"{prefix}: unknown route decision {decision!r}")
    allowed_decisions = {
        "proposed": {"unreviewed", "scout"},
        "active": {"advance", "branch", "deepen", "scout"},
        "suspended": {"suspend"},
        "refuted": {"hard_prune"},
        "merged": {"merge"},
        "completed": {"complete"},
    }
    if status in allowed_decisions and decision not in allowed_decisions[status]:
        errors.append(f"{prefix}: decision {decision!r} is inconsistent with status {status!r}")

    merge_target = route.get("merge_target_id")
    if merge_target is not None and not _is_nonempty_string(merge_target):
        errors.append(f"{prefix}: merge_target_id must be a nonempty string or null")
    if status == "merged" and merge_target is None:
        errors.append(f"{prefix}: merged route requires merge_target_id")
    if status != "merged" and merge_target is not None:
        errors.append(f"{prefix}: only a merged route may have merge_target_id")

    reopen_if = route.get("reopen_if")
    errors.extend(f"{prefix}: {error}" for error in _string_list_errors(reopen_if, "reopen_if"))
    if isinstance(reopen_if, list):
        if status == "suspended" and not reopen_if:
            errors.append(f"{prefix}: suspended route requires at least one reopen condition")
        if status != "suspended" and reopen_if:
            errors.append(f"{prefix}: only a suspended route may have reopen conditions")

    score = route.get("score")
    if not isinstance(score, Mapping):
        errors.append(f"{prefix}: score must be an object")
    else:
        missing_score = set(SCORE_FIELDS) - score.keys()
        if missing_score:
            errors.append(f"{prefix}: score missing fields {sorted(missing_score)}")
        for field in SCORE_FIELDS:
            value = score.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 2:
                errors.append(f"{prefix}: score.{field} must be an integer in [0, 2]")

    provenance = route.get("provenance")
    if not isinstance(provenance, Mapping):
        errors.append(f"{prefix}: provenance must be an object")
    else:
        search_mode = provenance.get("search_mode")
        initial_context = provenance.get("initial_context")
        route_card_hash = provenance.get("route_card_hash")
        route_card_origin = provenance.get("route_card_origin")
        agent_rollout_id = provenance.get("agent_rollout_id")
        agent_worker = provenance.get("agent_worker")
        agent_run_id = provenance.get("agent_run_id")
        independent_breadth_eligible = provenance.get("independent_breadth_eligible")
        resumed_from_checkpoint = provenance.get("resumed_from_checkpoint")
        source_card_path = provenance.get("source_card_path")
        source_result_path = provenance.get("source_result_path")
        source_result_hash = provenance.get("source_result_hash")
        source_review_path = provenance.get("source_review_path")
        route_review_hash = provenance.get("route_review_hash")
        reviewer_task_id = provenance.get("reviewer_task_id")
        reviewer_worker = provenance.get("reviewer_worker")
        reviewer_run_id = provenance.get("reviewer_run_id")
        reviewer_run_attestation = provenance.get("reviewer_run_attestation")
        source_prune_path = provenance.get("source_prune_path")
        route_prune_hash = provenance.get("route_prune_hash")
        prune_reviewer_task_id = provenance.get("prune_reviewer_task_id")
        prune_reviewer_worker = provenance.get("prune_reviewer_worker")
        prune_reviewer_run_id = provenance.get("prune_reviewer_run_id")
        prune_reviewer_run_attestation = provenance.get("prune_reviewer_run_attestation")
        prune_evidence_level = provenance.get("prune_evidence_level")
        prune_certificate_kind = provenance.get("prune_certificate_kind")
        prune_certificate_artifacts = provenance.get("prune_certificate_artifacts")
        if search_mode not in SEARCH_MODES:
            errors.append(f"{prefix}: unknown provenance.search_mode {search_mode!r}")
        if initial_context not in CONTEXT_MODES:
            errors.append(f"{prefix}: unknown provenance.initial_context {initial_context!r}")
        if route_card_hash is not None and (
            not isinstance(route_card_hash, str) or not SHA256_PATTERN.fullmatch(route_card_hash)
        ):
            errors.append(f"{prefix}: provenance.route_card_hash must be 64 lowercase hex characters or null")
        if search_mode == "sealed_breadth":
            if initial_context != "statement_only":
                errors.append(f"{prefix}: sealed_breadth must start from statement_only context")
            if not isinstance(route_card_hash, str) or not SHA256_PATTERN.fullmatch(route_card_hash):
                errors.append(f"{prefix}: sealed_breadth requires a committed route_card_hash")
            if route_card_origin not in ROUTE_CARD_ORIGINS:
                errors.append(
                    f"{prefix}: sealed_breadth must identify route_card_origin as "
                    "coordinator_precommit or agent_generated"
                )
            if route_card_origin == "agent_generated" and not _is_nonempty_string(agent_rollout_id):
                errors.append(f"{prefix}: agent_generated sealed card requires agent_rollout_id")
            if route_card_origin == "agent_generated" and not _is_nonempty_string(source_card_path):
                errors.append(f"{prefix}: agent_generated sealed card requires source_card_path")
            if route_card_origin == "agent_generated" and not _is_nonempty_string(agent_worker):
                errors.append(f"{prefix}: agent_generated sealed card requires agent_worker")
            if route_card_origin == "agent_generated" and not _is_nonempty_string(agent_run_id):
                errors.append(f"{prefix}: agent_generated sealed card requires agent_run_id")
            if route_card_origin == "agent_generated" and independent_breadth_eligible is not True:
                errors.append(
                    f"{prefix}: agent_generated sealed card must attest "
                    "independent_breadth_eligible=true"
                )
            if route_card_origin == "agent_generated" and resumed_from_checkpoint is not False:
                errors.append(
                    f"{prefix}: agent_generated sealed card cannot be checkpoint-resumed"
                )
            if route_card_origin == "agent_generated" and _is_nonempty_string(source_card_path):
                expected_source = f"research/routes/cards/{route_id}.json"
                if source_card_path != expected_source:
                    errors.append(
                        f"{prefix}: agent_generated source_card_path must be {expected_source!r}"
                    )
            if route_card_origin == "coordinator_precommit" and agent_rollout_id is not None:
                errors.append(
                    f"{prefix}: coordinator_precommit must not claim an agent_rollout_id"
                )
            if route_card_origin == "coordinator_precommit" and source_card_path is not None:
                errors.append(
                    f"{prefix}: coordinator_precommit must not claim an Agent source_card_path"
                )
            if route_card_origin == "coordinator_precommit" and (
                agent_worker is not None or agent_run_id is not None
            ):
                errors.append(
                    f"{prefix}: coordinator_precommit must not claim an Agent worker/run"
                )
        elif (
            route_card_origin is not None
            or agent_rollout_id is not None
            or source_card_path is not None
        ):
            errors.append(
                f"{prefix}: route-card origin, rollout, and source provenance are reserved for "
                "sealed_breadth"
            )
        if source_result_path is not None or source_result_hash is not None:
            if search_mode != "inherited_depth":
                errors.append(
                    f"{prefix}: continuation result provenance requires inherited_depth"
                )
            expected_result = f"research/routes/results/{route_id}.json"
            if source_result_path != expected_result:
                errors.append(
                    f"{prefix}: source_result_path must be {expected_result!r}"
                )
            if not isinstance(source_result_hash, str) or not SHA256_PATTERN.fullmatch(
                source_result_hash
            ):
                errors.append(
                    f"{prefix}: provenance.source_result_hash must be 64 lowercase hex characters"
                )
            if not _is_nonempty_string(agent_worker) or not _is_nonempty_string(agent_run_id):
                errors.append(
                    f"{prefix}: continuation result provenance requires agent_worker and agent_run_id"
                )
            if independent_breadth_eligible is not False:
                errors.append(
                    f"{prefix}: continuation result must attest "
                    "independent_breadth_eligible=false"
                )
            if not isinstance(resumed_from_checkpoint, bool):
                errors.append(
                    f"{prefix}: continuation result must record resumed_from_checkpoint as boolean"
                )
        elif (agent_worker is not None or agent_run_id is not None) and route_card_origin != "agent_generated":
            errors.append(
                f"{prefix}: Agent worker/run provenance requires a sealed card or continuation result"
            )
        review_values = (
            source_review_path,
            route_review_hash,
            reviewer_task_id,
            reviewer_worker,
            reviewer_run_id,
        )
        agent_created_route = route_card_origin == "agent_generated" or source_result_path is not None
        review_provenance_complete = all(
            _is_nonempty_string(value) for value in review_values
        ) and isinstance(reviewer_run_attestation, Mapping)
        if status in {"active", "completed"} and agent_created_route and not review_provenance_complete:
            errors.append(
                f"{prefix}: an Agent-created route cannot become active/completed before "
                "controlled target review"
            )
        if any(value is not None for value in review_values) or reviewer_run_attestation is not None:
            if not all(_is_nonempty_string(value) for value in review_values):
                errors.append(f"{prefix}: target-review provenance must be complete or absent")
            expected_review = f"research/routes/reviews/{route_id}.json"
            if source_review_path != expected_review:
                errors.append(
                    f"{prefix}: source_review_path must be {expected_review!r}"
                )
            if not isinstance(route_review_hash, str) or not SHA256_PATTERN.fullmatch(
                route_review_hash
            ):
                errors.append(
                    f"{prefix}: provenance.route_review_hash must be 64 lowercase hex characters"
                )
            if _is_nonempty_string(agent_worker) and reviewer_worker == agent_worker:
                errors.append(f"{prefix}: target reviewer must differ from the generating worker")
            if not isinstance(reviewer_run_attestation, Mapping) or set(
                reviewer_run_attestation
            ) != RUN_ATTESTATION_FIELDS or any(
                not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest)
                for digest in (
                    reviewer_run_attestation.values()
                    if isinstance(reviewer_run_attestation, Mapping)
                    else []
                )
            ):
                errors.append(
                    f"{prefix}: reviewer_run_attestation must contain the exact canonical "
                    "completed-run hashes"
                )
        prune_values = (
            source_prune_path,
            route_prune_hash,
            prune_reviewer_task_id,
            prune_reviewer_worker,
            prune_reviewer_run_id,
            prune_evidence_level,
            prune_certificate_kind,
        )
        if status == "refuted" or decision == "hard_prune":
            if not all(_is_nonempty_string(value) for value in prune_values) or not isinstance(
                prune_certificate_artifacts, list
            ) or not prune_certificate_artifacts or not isinstance(
                prune_reviewer_run_attestation, Mapping
            ):
                errors.append(
                    f"{prefix}: refuted/hard_prune requires complete controlled prune provenance"
                )
        elif (
            any(value is not None for value in prune_values)
            or prune_certificate_artifacts is not None
            or prune_reviewer_run_attestation is not None
        ):
            errors.append(f"{prefix}: prune provenance is reserved for refuted/hard_prune routes")
        if (
            any(value is not None for value in prune_values)
            or prune_certificate_artifacts is not None
            or prune_reviewer_run_attestation is not None
        ):
            expected_prune = f"research/routes/verdicts/{route_id}.json"
            if source_prune_path != expected_prune:
                errors.append(f"{prefix}: source_prune_path must be {expected_prune!r}")
            if not isinstance(route_prune_hash, str) or not SHA256_PATTERN.fullmatch(
                route_prune_hash
            ):
                errors.append(
                    f"{prefix}: provenance.route_prune_hash must be 64 lowercase hex characters"
                )
            if prune_evidence_level not in PRUNE_EVIDENCE_LEVELS:
                errors.append(f"{prefix}: prune_evidence_level must be E2 or higher")
            if prune_certificate_kind not in PRUNE_CERTIFICATE_KINDS:
                errors.append(f"{prefix}: prune_certificate_kind is invalid")
            if _is_nonempty_string(agent_worker) and prune_reviewer_worker == agent_worker:
                errors.append(f"{prefix}: prune reviewer must differ from the generating worker")
            if not isinstance(prune_reviewer_run_attestation, Mapping) or set(
                prune_reviewer_run_attestation
            ) != RUN_ATTESTATION_FIELDS or any(
                not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest)
                for digest in (
                    prune_reviewer_run_attestation.values()
                    if isinstance(prune_reviewer_run_attestation, Mapping)
                    else []
                )
            ):
                errors.append(
                    f"{prefix}: prune_reviewer_run_attestation must contain the exact "
                    "canonical completed-run hashes"
                )
            if isinstance(prune_certificate_artifacts, list):
                if not prune_certificate_artifacts:
                    errors.append(f"{prefix}: prune_certificate_artifacts must not be empty")
                for index, artifact in enumerate(prune_certificate_artifacts):
                    if not isinstance(artifact, Mapping) or set(artifact) != {"path", "sha256"}:
                        errors.append(
                            f"{prefix}: prune_certificate_artifacts[{index}] is malformed"
                        )
                        continue
                    expected_prefix = f"research/routes/certificates/{route_id}/"
                    if not _is_nonempty_string(artifact.get("path")) or not artifact[
                        "path"
                    ].startswith(expected_prefix):
                        errors.append(
                            f"{prefix}: prune certificate path must start with {expected_prefix!r}"
                        )
                    digest = artifact.get("sha256")
                    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                        errors.append(
                            f"{prefix}: prune certificate SHA-256 must be 64 lowercase hex characters"
                        )
    return errors


def _normalized_signature_text(value: Any) -> str:
    """Normalize only typography, never mathematical semantics."""

    return " ".join(str(value).casefold().split())


def exact_signature_key(route: Mapping[str, Any]) -> str:
    """Return the conservative duplicate key for a mathematical route.

    The key is namespaced by layer and target claim, then uses normalized exact
    text for representation, state, core lemma, and target-transfer edge.
    Failure descriptions and verifier implementations are evidence metadata:
    changing them does not manufacture a new route.  No fuzzy or embedding
    similarity is used.
    """

    signature = route.get("signature")
    if not isinstance(signature, Mapping) or any(field not in signature for field in SIGNATURE_FIELDS):
        raise RouteError(f"route {route.get('route_id', '<unknown>')} has no complete signature")
    canonical: dict[str, Any] = {
        "layer": route.get("layer"),
        "target_claim_id": route.get("target_claim_id"),
    }
    for field in DUPLICATE_SIGNATURE_FIELDS:
        canonical[field] = _normalized_signature_text(signature[field])
    return json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def find_exact_signature_duplicates(routes: Sequence[Mapping[str, Any]]) -> list[list[str]]:
    """Group route IDs with exactly matching mathematical signatures."""

    groups: dict[str, list[str]] = defaultdict(list)
    for route in routes:
        groups[exact_signature_key(route)].append(str(route.get("route_id", "<unknown>")))
    return [sorted(route_ids) for route_ids in groups.values() if len(route_ids) > 1]


def _cycle_errors(nodes: Mapping[str, Mapping[str, Any]]) -> list[str]:
    state: dict[str, int] = {}
    stack: list[str] = []
    reported: set[tuple[str, ...]] = set()
    errors: list[str] = []

    def visit(route_id: str) -> None:
        state[route_id] = 1
        stack.append(route_id)
        parents = nodes[route_id].get("parent_ids", [])
        if isinstance(parents, list):
            for parent_id in parents:
                if parent_id not in nodes:
                    continue
                if state.get(parent_id, 0) == 0:
                    visit(parent_id)
                elif state.get(parent_id) == 1:
                    start = stack.index(parent_id)
                    cycle = tuple(stack[start:] + [parent_id])
                    if cycle not in reported:
                        reported.add(cycle)
                        errors.append("route parent cycle detected: " + " -> ".join(cycle))
        stack.pop()
        state[route_id] = 2

    for route_id in nodes:
        if state.get(route_id, 0) == 0:
            visit(route_id)
    return errors


def validate_route_dag(routes: Sequence[Mapping[str, Any]]) -> list[str]:
    """Validate route nodes, their layered parent DAG, merges, and duplicates."""

    errors: list[str] = []
    for route in routes:
        errors.extend(validate_route_node(route))

    counts = Counter(str(route.get("route_id", "<unknown>")) for route in routes)
    for route_id, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"duplicate route_id {route_id!r} occurs {count} times")
    nodes: dict[str, Mapping[str, Any]] = {}
    for route in routes:
        route_id = route.get("route_id")
        if isinstance(route_id, str) and route_id not in nodes:
            nodes[route_id] = route

    children: dict[str, list[str]] = defaultdict(list)
    for route_id, route in nodes.items():
        layer = route.get("layer")
        parents = route.get("parent_ids")
        if not isinstance(parents, list) or layer not in LAYER_INDEX:
            continue
        if layer == "L0" and parents:
            errors.append(f"{route_id}: L0 target route must not have parents")
        if layer != "L0" and not parents:
            errors.append(f"{route_id}: {layer} route requires a parent in {LAYERS[LAYER_INDEX[layer] - 1]}")
        expected_parent_layer = LAYERS[LAYER_INDEX[layer] - 1] if layer != "L0" else None
        for parent_id in parents:
            parent = nodes.get(parent_id)
            if parent is None:
                errors.append(f"{route_id}: unknown parent route {parent_id!r}")
                continue
            children[parent_id].append(route_id)
            if expected_parent_layer is not None and parent.get("layer") != expected_parent_layer:
                errors.append(
                    f"{route_id}: parent {parent_id} must be in {expected_parent_layer}, "
                    f"not {parent.get('layer')}"
                )
    errors.extend(_cycle_errors(nodes))

    for route_id, route in nodes.items():
        if route.get("status") != "merged":
            continue
        target_id = route.get("merge_target_id")
        if target_id == route_id:
            errors.append(f"{route_id}: route cannot merge into itself")
            continue
        target = nodes.get(target_id) if isinstance(target_id, str) else None
        if target is None:
            errors.append(f"{route_id}: unknown merge target {target_id!r}")
            continue
        if target.get("status") in {"merged", "refuted"}:
            errors.append(f"{route_id}: merge target {target_id} must be a live canonical route")
        if route.get("layer") != target.get("layer"):
            errors.append(f"{route_id}: merge target {target_id} must be in the same layer")
        try:
            same_signature = exact_signature_key(route) == exact_signature_key(target)
        except RouteError:
            same_signature = False
        if not same_signature:
            errors.append(f"{route_id}: merge target {target_id} must have the exact same signature")
        if children.get(route_id):
            errors.append(
                f"{route_id}: merged route still has children {sorted(children[route_id])}; "
                "redirect them to the canonical route"
            )

    signature_groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for route in routes:
        try:
            signature_groups[exact_signature_key(route)].append(route)
        except RouteError:
            continue
    for group in signature_groups.values():
        if len(group) < 2:
            continue
        canonical = [route for route in group if route.get("status") != "merged"]
        group_ids = sorted(str(route.get("route_id")) for route in group)
        if len(canonical) != 1:
            errors.append(
                "unresolved exact-signature duplicate routes "
                f"{group_ids}; retain one canonical route and merge the others"
            )
            continue
        canonical_id = canonical[0].get("route_id")
        for route in group:
            if route is canonical[0]:
                continue
            if route.get("status") != "merged" or route.get("merge_target_id") != canonical_id:
                errors.append(
                    f"{route.get('route_id')}: exact duplicate must merge into canonical route {canonical_id}"
                )
    return errors


def can_reopen(route: Mapping[str, Any], satisfied_conditions: Iterable[str]) -> bool:
    """Return whether every declared condition for a suspended route is met.

    Refuted routes are never reopened in place: a materially revised statement
    is a new sibling or child node, preserving the exact counterexample record.
    """

    conditions = route.get("reopen_if")
    if route.get("status") != "suspended" or route.get("decision") != "suspend":
        return False
    if not isinstance(conditions, list) or not conditions:
        return False
    satisfied = set(satisfied_conditions)
    return all(condition in satisfied for condition in conditions)


def recommend_route(
    route: Mapping[str, Any], policy: Mapping[str, Any] | None = None
) -> str:
    """Recommend ``deepen``, ``scout``, or ``suspend`` from the five RPCD scores.

    A hard-pruned/refuted route is vetoed regardless of score.  Failed target
    transfer or an exact counterexample (zero counterexample resistance) also
    vetoes further investment; this prevents a strong but irrelevant matrix
    certificate from absorbing the finite-time RPCD portfolio.
    """

    chosen_policy = _deep_merge_defaults(DEFAULT_PORTFOLIO_POLICY, policy or {})
    policy_errors = validate_portfolio_policy(chosen_policy)
    if policy_errors:
        raise RouteError("invalid portfolio policy: " + "; ".join(policy_errors))
    score = route.get("score")
    if not isinstance(score, Mapping) or any(
        not isinstance(score.get(field), int)
        or isinstance(score.get(field), bool)
        or not 0 <= score.get(field) <= 2
        for field in SCORE_FIELDS
    ):
        raise RouteError(f"route {route.get('route_id', '<unknown>')} has an invalid score")

    if route.get("decision") == "hard_prune" or route.get("status") in {
        "refuted",
        "merged",
        "completed",
        "suspended",
    }:
        return "suspend"
    if route.get("status") == "proposed":
        # A high coordinator score does not make an unreviewed mathematical
        # node deep work. It must first earn an active/scout transition.
        return "scout"
    recommendation = chosen_policy["recommendation"]
    if any(score[field] <= 0 for field in recommendation["mandatory_positive"]):
        return "suspend"
    total = sum(score[field] for field in SCORE_FIELDS)
    if total >= recommendation["deepen_min_total"]:
        return "deepen"
    if total >= recommendation["scout_min_total"]:
        return "scout"
    return "suspend"


def is_sealed_breadth_route(route: Mapping[str, Any]) -> bool:
    """Return whether a sealed card was actually generated by an isolated rollout.

    A coordinator-authored precommit is useful for planning but is not an
    independent mathematical sample and therefore contributes zero realized
    breadth to the portfolio audit.
    """

    provenance = route.get("provenance")
    return bool(
        isinstance(provenance, Mapping)
        and provenance.get("search_mode") == "sealed_breadth"
        and provenance.get("initial_context") == "statement_only"
        and provenance.get("route_card_origin") == "agent_generated"
        and _is_nonempty_string(provenance.get("agent_rollout_id"))
        and _is_nonempty_string(provenance.get("agent_worker"))
        and _is_nonempty_string(provenance.get("agent_run_id"))
        and provenance.get("independent_breadth_eligible") is True
        and provenance.get("resumed_from_checkpoint") is False
        and _is_nonempty_string(provenance.get("source_card_path"))
        and isinstance(provenance.get("route_card_hash"), str)
        and SHA256_PATTERN.fullmatch(provenance["route_card_hash"])
        and _is_nonempty_string(provenance.get("source_review_path"))
        and isinstance(provenance.get("route_review_hash"), str)
        and SHA256_PATTERN.fullmatch(provenance["route_review_hash"])
        and _is_nonempty_string(provenance.get("reviewer_task_id"))
        and _is_nonempty_string(provenance.get("reviewer_worker"))
        and _is_nonempty_string(provenance.get("reviewer_run_id"))
        and isinstance(provenance.get("reviewer_run_attestation"), Mapping)
        and set(provenance["reviewer_run_attestation"]) == RUN_ATTESTATION_FIELDS
        and provenance.get("reviewer_worker") != provenance.get("agent_worker")
    )


def active_frontier_routes(
    routes: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None
) -> list[Mapping[str, Any]]:
    """Return eligible active nodes with no eligible active child.

    A single mathematical route often has simultaneous L1, L2, and L3 records.
    Only its deepest active frontier node counts as one portfolio branch.
    """

    chosen_policy = _deep_merge_defaults(DEFAULT_PORTFOLIO_POLICY, policy or {})
    policy_errors = validate_portfolio_policy(chosen_policy)
    if policy_errors:
        raise RouteError("invalid portfolio policy: " + "; ".join(policy_errors))
    settings = chosen_policy["portfolio"]
    eligible = [
        route
        for route in routes
        if route.get("status") in settings["active_statuses"]
        and route.get("layer") in settings["layers"]
    ]
    eligible_ids = {
        route.get("route_id") for route in eligible if isinstance(route.get("route_id"), str)
    }
    has_active_child: set[str] = set()
    for route in eligible:
        parents = route.get("parent_ids")
        if not isinstance(parents, list):
            continue
        has_active_child.update(parent_id for parent_id in parents if parent_id in eligible_ids)
    return [route for route in eligible if route.get("route_id") not in has_active_child]


def _has_agent_generated_sealed_lineage(
    route: Mapping[str, Any], nodes: Mapping[str, Mapping[str, Any]]
) -> bool:
    pending = [route]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        route_id = current.get("route_id")
        if isinstance(route_id, str):
            if route_id in visited:
                continue
            visited.add(route_id)
        if is_sealed_breadth_route(current):
            return True
        parents = current.get("parent_ids")
        if isinstance(parents, list):
            pending.extend(nodes[parent_id] for parent_id in parents if parent_id in nodes)
    return False


def _portfolio_findings(
    routes: Sequence[Mapping[str, Any]], chosen_policy: Mapping[str, Any]
) -> tuple[list[Mapping[str, Any]], list[dict[str, Any]]]:
    """Return the active frontier and structured breadth-gate findings."""

    settings = chosen_policy["portfolio"]
    active = active_frontier_routes(routes, chosen_policy)
    nodes = {
        route["route_id"]: route
        for route in routes
        if isinstance(route.get("route_id"), str)
    }
    findings: list[dict[str, Any]] = []
    if settings["require_sealed_breadth"] and not any(
        _has_agent_generated_sealed_lineage(route, nodes) for route in active
    ):
        findings.append(
            {
                "code": "missing_agent_generated_sealed_breadth",
                "message": (
                    "active RPCD frontier has no route descended from an agent-generated "
                    "sealed-breadth card committed from statement-only context"
                ),
            }
        )

    minimum = settings["concentration_min_routes"]
    if len(active) >= minimum:
        family_counts = Counter(str(route.get("method_family", "")).strip() for route in active)
        maximum = float(settings["max_method_family_fraction"])
        for family, count in sorted(family_counts.items()):
            fraction = count / len(active)
            if fraction > maximum + 1e-12:
                findings.append(
                    {
                        "code": "method_family_concentration",
                        "method_family": family,
                        "count": count,
                        "frontier_count": len(active),
                        "fraction": fraction,
                        "cap": maximum,
                        "message": (
                            f"method family {family!r} occupies {count}/{len(active)} active "
                            f"frontier routes ({fraction:.3f}), above policy cap {maximum:.3f}"
                        ),
                    }
                )

        target_counts = Counter(str(route.get("target_claim_id", "")).strip() for route in active)
        target_maximum = float(settings["max_limited_target_claim_fraction"])
        for claim_id in settings["concentration_limited_target_claim_ids"]:
            count = target_counts.get(claim_id, 0)
            fraction = count / len(active)
            if fraction > target_maximum + 1e-12:
                findings.append(
                    {
                        "code": "target_certificate_concentration",
                        "target_claim_id": claim_id,
                        "count": count,
                        "frontier_count": len(active),
                        "fraction": fraction,
                        "cap": target_maximum,
                        "message": (
                            f"target/certificate claim {claim_id!r} occupies {count}/{len(active)} "
                            f"active frontier routes ({fraction:.3f}), above policy cap "
                            f"{target_maximum:.3f}"
                        ),
                    }
                )
    return active, findings


def audit_portfolio(
    routes: Sequence[Mapping[str, Any]], policy: Mapping[str, Any] | None = None
) -> list[str]:
    """Audit active RPCD routes for realized breadth and concentration."""

    chosen_policy = _deep_merge_defaults(DEFAULT_PORTFOLIO_POLICY, policy or {})
    policy_errors = validate_portfolio_policy(chosen_policy)
    if policy_errors:
        return ["invalid portfolio policy: " + "; ".join(policy_errors)]
    try:
        _, findings = _portfolio_findings(routes, chosen_policy)
    except RouteError as error:
        return [str(error)]
    return [finding["message"] for finding in findings]


def plan_route_allocation(
    routes: Sequence[Mapping[str, Any]],
    policy: Mapping[str, Any] | None = None,
    *,
    effective_breadth: float | None = None,
    breadth_review_kind: str | None = None,
) -> dict[str, Any]:
    """Build an auditable breadth/depth allocation recommendation.

    Global breadth gates have priority over local scores.  Otherwise the plan
    scores only deepest active frontier leaves and returns *all* tied leaders;
    it never manufactures a unique winner.
    """

    chosen_policy = _deep_merge_defaults(DEFAULT_PORTFOLIO_POLICY, policy or {})
    policy_errors = validate_portfolio_policy(chosen_policy)
    if policy_errors:
        raise RouteError("invalid portfolio policy: " + "; ".join(policy_errors))
    dag_errors = validate_route_dag(routes)
    if dag_errors:
        raise RouteError("cannot allocate an invalid route DAG: " + "; ".join(dag_errors))

    frontier, findings = _portfolio_findings(routes, chosen_policy)
    route_nodes = {
        str(route.get("route_id")): route
        for route in routes
        if isinstance(route.get("route_id"), str)
    }
    realized_agent_breadth = any(
        _has_agent_generated_sealed_lineage(route, route_nodes) for route in frontier
    )
    if realized_agent_breadth and effective_breadth is None:
        findings.append(
            {
                "code": "missing_post_rollout_breadth_review",
                "message": (
                    "agent-generated sealed breadth is active, but no complete current-frontier "
                    "post_rollout_review B_eff snapshot was supplied"
                ),
            }
        )
    elif realized_agent_breadth and breadth_review_kind != "post_rollout_review":
        findings.append(
            {
                "code": "stale_or_planning_breadth_review",
                "breadth_review_kind": breadth_review_kind,
                "message": (
                    "agent-generated sealed breadth requires a fresh post_rollout_review; "
                    "a planning estimate or an untyped scalar cannot authorize depth allocation"
                ),
            }
        )
    if effective_breadth is not None:
        if (
            not isinstance(effective_breadth, (int, float))
            or isinstance(effective_breadth, bool)
            or not math.isfinite(float(effective_breadth))
            or float(effective_breadth) <= 0.0
        ):
            raise RouteError("effective_breadth must be a finite number > 0")
        minimum_breadth = float(chosen_policy["portfolio"]["min_effective_breadth"])
        if frontier and float(effective_breadth) < minimum_breadth:
            findings.append(
                {
                    "code": "low_effective_breadth",
                    "effective_breadth": float(effective_breadth),
                    "frontier_count": len(frontier),
                    "minimum": minimum_breadth,
                    "message": (
                        f"reviewer-declared effective breadth {float(effective_breadth):.3f} "
                        f"is below policy minimum {minimum_breadth:.3f} for "
                        f"{len(frontier)} active frontier routes"
                    ),
                }
            )
    frontier_rows: list[dict[str, Any]] = []
    for route in sorted(frontier, key=lambda node: str(node.get("route_id"))):
        score = route["score"]
        frontier_rows.append(
            {
                "route_id": route["route_id"],
                "layer": route["layer"],
                "method_family": route["method_family"],
                "target_claim_id": route["target_claim_id"],
                "score_total": sum(score[field] for field in SCORE_FIELDS),
                "recommendation": recommend_route(route, chosen_policy),
            }
        )

    if findings:
        limited_claims = set(
            chosen_policy["portfolio"]["concentration_limited_target_claim_ids"]
        )
        anchors = sorted(
            str(route["route_id"])
            for route in routes
            if route.get("layer") == "L0"
            and route.get("status") in chosen_policy["portfolio"]["active_statuses"]
            and route.get("target_claim_id") not in limited_claims
        )
        if not anchors:
            anchors = sorted(
                str(route["route_id"])
                for route in routes
                if route.get("layer") == "L0"
                and route.get("status") in chosen_policy["portfolio"]["active_statuses"]
            )
        return {
            "schema_version": "1.0",
            "action": "expand_breadth",
            "candidate_route_ids": anchors,
            "tie": len(anchors) > 1,
            "selection_rule": "global_breadth_gate_before_local_score",
            "effective_breadth": effective_breadth,
            "breadth_review_kind": breadth_review_kind,
            "breadth_findings": findings,
            "frontier": frontier_rows,
        }

    action = "suspend"
    candidates: list[dict[str, Any]] = []
    for recommendation in ("deepen", "scout", "suspend"):
        eligible = [row for row in frontier_rows if row["recommendation"] == recommendation]
        if eligible:
            action = recommendation
            best_score = max(row["score_total"] for row in eligible)
            candidates = [row for row in eligible if row["score_total"] == best_score]
            break
    route_by_id = {
        str(route.get("route_id")): route
        for route in frontier
        if isinstance(route.get("route_id"), str)
    }
    protected_scouts = sorted(
        row["route_id"]
        for row in frontier_rows
        if row["target_claim_id"] == "C050"
        and row["recommendation"] in {"scout", "deepen"}
        and is_sealed_breadth_route(route_by_id[row["route_id"]])
    )
    primary_ids = [row["route_id"] for row in candidates]
    combined_ids = list(primary_ids)
    for route_id in protected_scouts:
        if route_id not in combined_ids:
            combined_ids.append(route_id)
    if protected_scouts and set(combined_ids) != set(primary_ids):
        action = "mixed"
        selection_rule = (
            "highest_score_on_deepest_active_frontier_plus_protected_agent_generated_"
            "direct_target_scouts"
        )
    else:
        selection_rule = "highest_score_on_deepest_active_frontier_without_tie_break"
    return {
        "schema_version": "1.0",
        "action": action,
        "candidate_route_ids": combined_ids,
        "depth_candidate_route_ids": primary_ids,
        "protected_scout_route_ids": protected_scouts,
        "tie": len(candidates) > 1,
        "selection_rule": selection_rule,
        "effective_breadth": effective_breadth,
        "breadth_review_kind": breadth_review_kind,
        "breadth_findings": [],
        "frontier": frontier_rows,
    }


def _audit_tracked_route_review(
    root: Path, route: Mapping[str, Any], provenance: Mapping[str, Any]
) -> list[str]:
    """Re-hash one optional target review for sealed or continuation routes."""

    route_id = str(route.get("route_id", "<unknown>"))
    review_raw = provenance.get("source_review_path")
    review_hash = provenance.get("route_review_hash")
    if review_raw is None and review_hash is None:
        return []
    errors: list[str] = []
    expected_review = f"research/routes/reviews/{route_id}.json"
    if review_raw != expected_review:
        return [f"{route_id}: source_review_path must be tracked at {expected_review!r}"]
    try:
        review_source = _recorded_repo_path(
            root, review_raw, f"{route_id} source_review_path"
        )
    except RouteError as error:
        return [str(error)]
    if not review_source.is_file():
        return [f"{route_id}: tracked target review is missing: {review_raw}"]
    try:
        actual_review_hash = _sha256_path(review_source)
    except RouteError as error:
        return [str(error)]
    if review_hash != actual_review_hash:
        return [
            f"{route_id}: tracked target review SHA-256 {actual_review_hash} does not "
            f"match provenance {review_hash}"
        ]
    try:
        review = _read_json_object(review_source, f"{route_id} tracked target review")
    except RouteError as error:
        return [str(error)]
    if review.get("route_id") != route_id:
        errors.append(f"{route_id}: tracked target review names a different route")
    if review.get("route_card_sha256") != provenance.get("route_card_hash"):
        errors.append(f"{route_id}: tracked target review names a different route card")
    if review.get("target_claim_id") != route.get("target_claim_id"):
        errors.append(f"{route_id}: tracked target review names a different target claim")
    if review.get("reviewer_task_id") != provenance.get("reviewer_task_id"):
        errors.append(f"{route_id}: reviewer task differs from tracked target review")
    if review.get("reviewer_worker") != provenance.get("reviewer_worker") or review.get(
        "reviewer_run_id"
    ) != provenance.get("reviewer_run_id"):
        errors.append(f"{route_id}: reviewer identity differs from tracked target review")
    attestation = provenance.get("reviewer_run_attestation")
    if not isinstance(attestation, Mapping) or set(attestation) != RUN_ATTESTATION_FIELDS:
        errors.append(f"{route_id}: target reviewer run attestation is malformed")
    reviewer_task_id = provenance.get("reviewer_task_id")
    reviewer_run_id = provenance.get("reviewer_run_id")
    if _is_nonempty_string(reviewer_task_id) and _is_nonempty_string(reviewer_run_id):
        try:
            reviewer_run = _recorded_repo_path(
                root,
                f"runs/{reviewer_task_id}/{reviewer_run_id}",
                f"{route_id} target reviewer run",
            )
            if reviewer_run.exists():
                invocation = _read_json_object(
                    reviewer_run / "invocation.json", f"{route_id} target reviewer invocation"
                )
                if invocation.get("rollout_strategy") is not None or invocation.get(
                    "worker"
                ) != provenance.get("reviewer_worker"):
                    errors.append(
                        f"{route_id}: target reviewer identity does not match its standalone run"
                    )
                from .fanout import _validated_run_attestation
                from .protocol import ProtocolError

                try:
                    _validated_run_attestation(
                        root,
                        str(reviewer_task_id),
                        None,
                        reviewer_run,
                        recorded=dict(attestation) if isinstance(attestation, Mapping) else None,
                    )
                except (OSError, ProtocolError, ValueError) as error:
                    errors.append(
                        f"{route_id}: target reviewer run no longer matches its canonical "
                        f"attestation: {error}"
                    )
        except RouteError as error:
            errors.append(str(error))
    return errors


def _audit_tracked_prune_verdict(
    root: Path, route: Mapping[str, Any], provenance: Mapping[str, Any]
) -> list[str]:
    """Re-hash and rebind one controlled route-local hard-prune verdict."""

    route_id = str(route.get("route_id", "<unknown>"))
    raw = provenance.get("source_prune_path")
    recorded_hash = provenance.get("route_prune_hash")
    if raw is None and recorded_hash is None:
        return []
    expected = f"research/routes/verdicts/{route_id}.json"
    if raw != expected:
        return [f"{route_id}: source_prune_path must be tracked at {expected!r}"]
    try:
        source = _recorded_repo_path(root, raw, f"{route_id} source_prune_path")
    except RouteError as error:
        return [str(error)]
    if not source.is_file():
        return [f"{route_id}: tracked prune verdict is missing: {raw}"]
    try:
        actual_hash = _sha256_path(source)
    except RouteError as error:
        return [str(error)]
    if actual_hash != recorded_hash:
        return [
            f"{route_id}: tracked prune verdict SHA-256 {actual_hash} does not match "
            f"provenance {recorded_hash}"
        ]
    try:
        verdict = _read_json_object(source, f"{route_id} tracked prune verdict")
    except RouteError as error:
        return [str(error)]
    errors: list[str] = []
    if verdict.get("kind") != "rpcd-route-prune-verdict" or verdict.get("route_id") != route_id:
        errors.append(f"{route_id}: tracked prune verdict names a different route or kind")
    if verdict.get("route_card_sha256") != provenance.get("route_card_hash"):
        errors.append(f"{route_id}: tracked prune verdict names a different route card")
    if verdict.get("target_claim_id") != route.get("target_claim_id"):
        errors.append(f"{route_id}: tracked prune verdict names a different target claim")
    if verdict.get("route_local_statement") != route.get("statement"):
        errors.append(f"{route_id}: tracked prune verdict names a different route-local statement")
    if verdict.get("master_claim_affected") is not False:
        errors.append(f"{route_id}: tracked prune verdict improperly affects a master claim")
    if verdict.get("reviewer_task_id") != provenance.get("prune_reviewer_task_id"):
        errors.append(f"{route_id}: prune reviewer task differs from tracked verdict")
    if verdict.get("reviewer_worker") != provenance.get(
        "prune_reviewer_worker"
    ) or verdict.get("reviewer_run_id") != provenance.get("prune_reviewer_run_id"):
        errors.append(f"{route_id}: prune reviewer identity differs from tracked verdict")
    if verdict.get("evidence_level") != provenance.get("prune_evidence_level"):
        errors.append(f"{route_id}: prune evidence level differs from tracked verdict")
    if verdict.get("certificate_kind") != provenance.get("prune_certificate_kind"):
        errors.append(f"{route_id}: prune certificate kind differs from tracked verdict")
    attestation = provenance.get("prune_reviewer_run_attestation")
    if not isinstance(attestation, Mapping) or set(attestation) != RUN_ATTESTATION_FIELDS:
        errors.append(f"{route_id}: prune reviewer run attestation is malformed")
    reviewer_task_id = provenance.get("prune_reviewer_task_id")
    reviewer_run_id = provenance.get("prune_reviewer_run_id")
    if _is_nonempty_string(reviewer_task_id) and _is_nonempty_string(reviewer_run_id):
        try:
            reviewer_run = _recorded_repo_path(
                root,
                f"runs/{reviewer_task_id}/{reviewer_run_id}",
                f"{route_id} prune reviewer run",
            )
            # Portable route memory may intentionally omit runs/.  If the run
            # is present, however, it must still match the stored canonical
            # attestation; a partial or tampered local run is never ignored.
            if reviewer_run.exists():
                invocation = _read_json_object(
                    reviewer_run / "invocation.json", f"{route_id} prune reviewer invocation"
                )
                if invocation.get("rollout_strategy") is not None or invocation.get(
                    "worker"
                ) != provenance.get("prune_reviewer_worker"):
                    errors.append(
                        f"{route_id}: prune reviewer identity does not match its standalone run"
                    )
                from .fanout import _validated_run_attestation
                from .protocol import ProtocolError

                try:
                    _validated_run_attestation(
                        root,
                        str(reviewer_task_id),
                        None,
                        reviewer_run,
                        recorded=dict(attestation) if isinstance(attestation, Mapping) else None,
                    )
                except (OSError, ProtocolError, ValueError) as error:
                    errors.append(
                        f"{route_id}: prune reviewer run no longer matches its canonical "
                        f"attestation: {error}"
                    )
        except RouteError as error:
            errors.append(str(error))
    source_artifacts = verdict.get("certificate_artifacts")
    artifacts = provenance.get("prune_certificate_artifacts")
    if not isinstance(source_artifacts, list) or not source_artifacts:
        errors.append(f"{route_id}: tracked prune verdict has no certificate artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append(f"{route_id}: prune provenance has no tracked certificate artifacts")
    else:
        if isinstance(source_artifacts, list) and len(artifacts) != len(source_artifacts):
            errors.append(
                f"{route_id}: tracked certificate count differs from the prune verdict"
            )
        for record in artifacts:
            if not isinstance(record, Mapping):
                errors.append(f"{route_id}: tracked prune certificate record is malformed")
                continue
            artifact_raw = record.get("path")
            try:
                artifact = _recorded_repo_path(
                    root, artifact_raw, f"{route_id} prune certificate artifact"
                )
                if not artifact.is_file():
                    errors.append(
                        f"{route_id}: tracked prune certificate artifact is missing: {artifact_raw}"
                    )
                elif record.get("sha256") != _sha256_path(artifact):
                    errors.append(
                        f"{route_id}: tracked prune certificate SHA-256 does not match provenance: {artifact_raw}"
                    )
            except RouteError as error:
                errors.append(str(error))
    return errors


def audit_agent_generated_provenance(
    root: Path, routes: Sequence[Mapping[str, Any]]
) -> list[str]:
    """Re-hash tracked Agent cards/results/reviews and compare their route nodes."""

    root = Path(root).resolve()
    errors: list[str] = []
    for route in routes:
        provenance = route.get("provenance")
        if not isinstance(provenance, Mapping):
            continue
        route_id = str(route.get("route_id", "<unknown>"))
        errors.extend(_audit_tracked_route_review(root, route, provenance))
        errors.extend(_audit_tracked_prune_verdict(root, route, provenance))
        result_raw = provenance.get("source_result_path")
        if result_raw is not None:
            expected_result = f"research/routes/results/{route_id}.json"
            if result_raw != expected_result:
                errors.append(
                    f"{route_id}: source_result_path must be tracked at {expected_result!r}"
                )
            else:
                try:
                    result_source = _recorded_repo_path(
                        root, result_raw, f"{route_id} source_result_path"
                    )
                    if not result_source.is_file():
                        errors.append(
                            f"{route_id}: tracked continuation result is missing: {result_raw}"
                        )
                    elif provenance.get("source_result_hash") != _sha256_path(result_source):
                        errors.append(
                            f"{route_id}: tracked continuation result SHA-256 does not match provenance"
                        )
                    else:
                        result = _read_json_object(
                            result_source, f"{route_id} tracked continuation result"
                        )
                        avenues = result.get("iteration", {}).get("avenues")
                        matches = [
                            avenue
                            for avenue in avenues
                            if isinstance(avenues, list)
                            and isinstance(avenue, Mapping)
                            and avenue.get("route_id") == route_id
                        ] if isinstance(avenues, list) else []
                        if len(matches) != 1:
                            errors.append(
                                f"{route_id}: tracked continuation result must contain exactly one named child avenue"
                            )
                        else:
                            avenue = matches[0]
                            expected_signature = {
                                "representation": avenue.get("representation"),
                                "state_or_invariant": avenue.get("state_or_invariant"),
                                "core_candidate_lemma": avenue.get("core_candidate_lemma"),
                                "information_retained": avenue.get("information_retained"),
                                "information_discarded": avenue.get("information_discarded"),
                                "target_implication": avenue.get("target_implication"),
                                "known_failure_mode": avenue.get("predicted_failure"),
                                "verifier_class": (
                                    "Agent-declared first falsifier: "
                                    f"{avenue.get('falsifier')}"
                                ),
                            }
                            if route.get("method_family") != avenue.get("method_family"):
                                errors.append(
                                    f"{route_id}: method_family differs from the tracked continuation result"
                                )
                            if route.get("parent_ids") != avenue.get("parent_route_ids"):
                                errors.append(
                                    f"{route_id}: parent_ids differ from the tracked continuation result"
                                )
                            if route.get("layer") != avenue.get("next_layer"):
                                errors.append(
                                    f"{route_id}: layer differs from the tracked continuation result"
                                )
                            if route.get("statement") != avenue.get("core_candidate_lemma"):
                                errors.append(
                                    f"{route_id}: statement differs from the tracked continuation result"
                                )
                            if route.get("signature") != expected_signature:
                                errors.append(
                                    f"{route_id}: mathematical signature differs from the tracked continuation result"
                                )
                except RouteError as error:
                    errors.append(str(error))
        if provenance.get("route_card_origin") != "agent_generated":
            continue
        source_raw = provenance.get("source_card_path")
        if not _is_nonempty_string(source_raw):
            errors.append(f"{route_id}: agent-generated provenance has no source_card_path")
            continue
        expected_relative = f"research/routes/cards/{route_id}.json"
        if source_raw != expected_relative:
            errors.append(
                f"{route_id}: source_card_path must be tracked at {expected_relative!r}"
            )
            continue
        try:
            source = _recorded_repo_path(root, source_raw, f"{route_id} source_card_path")
        except RouteError as error:
            errors.append(str(error))
            continue
        if not source.is_file():
            errors.append(f"{route_id}: tracked source card is missing: {source_raw}")
            continue
        expected_hash = provenance.get("route_card_hash")
        try:
            actual_hash = _sha256_path(source)
        except RouteError as error:
            errors.append(str(error))
            continue
        if expected_hash != actual_hash:
            errors.append(
                f"{route_id}: tracked source card SHA-256 {actual_hash} does not match "
                f"provenance {expected_hash}"
            )
            continue
        try:
            card = _read_json_object(source, f"{route_id} tracked source card")
        except RouteError as error:
            errors.append(str(error))
            continue
        expected_signature = {
            "representation": card.get("representation"),
            "state_or_invariant": card.get("state_or_invariant"),
            "core_candidate_lemma": card.get("core_candidate_lemma"),
            "information_retained": card.get("information_retained"),
            "information_discarded": card.get("information_discarded"),
            "target_implication": card.get("target_implication"),
            "known_failure_mode": card.get("predicted_failure"),
            "verifier_class": f"Agent-declared first falsifier: {card.get('falsifier')}",
        }
        if route.get("method_family") != card.get("method_family"):
            errors.append(f"{route_id}: method_family differs from the tracked source card")
        if route.get("parent_ids") != card.get("parent_route_ids"):
            errors.append(f"{route_id}: parent_ids differ from the tracked source card")
        if provenance.get("agent_rollout_id") != card.get("rollout_id"):
            errors.append(f"{route_id}: agent_rollout_id differs from the tracked source card")
        if route.get("statement") != card.get("core_candidate_lemma"):
            errors.append(f"{route_id}: statement differs from the tracked source card")
        if route.get("signature") != expected_signature:
            errors.append(f"{route_id}: mathematical signature differs from the tracked source card")
    return errors


def audit_route_repository(root: Path) -> list[str]:
    """Load and audit the optional route registry and its repository policy."""

    routes = load_route_nodes(root)
    policy = load_portfolio_policy(root)
    return (
        validate_route_dag(routes)
        + audit_agent_generated_provenance(root, routes)
        + audit_portfolio(routes, policy)
    )
