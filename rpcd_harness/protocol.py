"""Task, result, claim-ledger, and checkpoint validation."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping


EVIDENCE_RANK = {f"E{index}": index for index in range(7)}
RESULT_STATUSES = {
    "open_conjecture",
    "idea",
    "numerical_observation",
    "finite_verified",
    "proof_candidate",
    "theorem_candidate",
    "refuted",
    "external_theorem",
}
ROLES = {"librarian", "researcher", "experimentalist", "explorer", "skeptic", "reproducer", "formalizer"}
RESEARCH_MODES = {"sealed_breadth", "continuation_depth", "critic_validation"}
CONTEXT_MODES = {"statement_only", "declared_inputs", "full_history"}
DEPENDENCY_MODES = {"latest_validated_run", "complete_validated_fanout"}
ROUTE_ID_PATTERN = re.compile(r"^R[0-9]{3}-[a-z0-9-]+$")
MASTER_CLAIM_IDS = {"C001", "C050", "C051"}


class ProtocolError(ValueError):
    pass


DEFAULT_ITERATION_POLICY = {
    "schema_version": "1.0",
    "minimum_active_minutes_per_worker": 120,
    "checkpoint_interval_minutes": 30,
    "minimum_distinct_avenues": 3,
    "minimum_failed_or_stress_tests": 2,
}


def find_root(start: Path | None = None) -> Path:
    candidate = (start or Path.cwd()).resolve()
    for directory in (candidate, *candidate.parents):
        if (directory / "pyproject.toml").is_file() and (directory / "research" / "tasks").is_dir():
            return directory
    raise ProtocolError("could not locate the RPCD harness root")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProtocolError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(data, dict):
        raise ProtocolError(f"expected a JSON object in {path}")
    return data


def load_iteration_policy(root: Path) -> dict[str, Any]:
    """Load and validate the global deep-iteration policy.

    The policy is deliberately repository-owned so a portable bundle carries the
    same research-time contract to another account.
    """
    path = root / "research" / "iteration_policy.json"
    policy = read_json(path) if path.is_file() else dict(DEFAULT_ITERATION_POLICY)
    if policy.get("schema_version") != "1.0":
        raise ProtocolError("unsupported iteration policy schema version")
    integer_fields = {
        "minimum_active_minutes_per_worker": 120,
        "checkpoint_interval_minutes": 5,
        "minimum_distinct_avenues": 1,
        "minimum_failed_or_stress_tests": 0,
    }
    for field, minimum in integer_fields.items():
        value = policy.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            raise ProtocolError(f"iteration policy {field} must be an integer >= {minimum}")
    return policy


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_source_snapshot(root: Path, task: dict[str, Any]) -> dict[str, Any]:
    """Return a portable hash tree for the task's research/code specification.

    The selection deliberately excludes dynamic ``runs/`` output.  It binds
    task inputs, the active prompt and policies, packaging constraints, harness
    and schema code, static task-verifier files, and an official fanout
    manifest when declared.  Missing optional fixed files are recorded so an
    account cannot silently add or remove one between rollout and merge.
    """

    root = root.resolve()
    selected: set[str] = set()
    missing: set[str] = set()

    def add_path(raw: str, *, record_missing: bool = True) -> None:
        if not _safe_relative_path(raw):
            raise ProtocolError(f"unsafe repository source path: {raw!r}")
        unresolved = root / raw
        if unresolved.is_symlink():
            raise ProtocolError(f"repository source cannot be a symbolic link: {raw}")
        candidate = unresolved.resolve()
        try:
            candidate.relative_to(root)
        except (OSError, ValueError) as error:
            raise ProtocolError(f"repository source escapes root: {raw}") from error
        canonical_requested = PurePosixPath(raw.replace("\\", "/")).as_posix()
        if not candidate.exists():
            if record_missing:
                missing.add(canonical_requested)
            return
        if candidate.relative_to(root).as_posix() != canonical_requested:
            raise ProtocolError(f"repository source path is noncanonical: {raw}")
        if candidate.is_file():
            selected.add(candidate.relative_to(root).as_posix())
            return
        if not candidate.is_dir():
            raise ProtocolError(f"repository source is not a file or directory: {raw}")
        for path in sorted(candidate.rglob("*")):
            if path.is_symlink():
                raise ProtocolError(
                    f"repository source tree cannot contain symbolic links: {raw}"
                )
            if path.is_file():
                selected.add(path.resolve().relative_to(root).as_posix())

    fixed_sources = {
        "AGENTS.md",
        "constraints.txt",
        "pyproject.toml",
        "requirements.txt",
        "prompts/common.md",
        f"prompts/{task['role']}.md",
        "research/iteration_policy.json",
        "research/portfolio_policy.json",
        f"research/tasks/{task['task_id']}.json",
    }
    for raw in sorted(fixed_sources):
        add_path(raw)
    for raw in task.get("inputs", []):
        add_path(raw)
    official_manifest = task.get("fanout_manifest")
    if isinstance(official_manifest, str):
        add_path(official_manifest)

    # Bind the executable harness and its JSON contracts without absorbing
    # machine-generated __pycache__ files into the portable snapshot.
    for pattern in ("rpcd_harness/**/*.py", "schemas/**/*.json"):
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                add_path(path.relative_to(root).as_posix(), record_missing=False)

    # Static repository files named directly by task verifier argv are part of
    # the trusted verifier. Dynamic {artifact_dir} controls are instead bound
    # by the result artifact and verifier-log attestations.
    for verifier in task.get("verifiers", []):
        command = verifier.get("command", []) if isinstance(verifier, dict) else []
        python_source_index = 2 if len(command) > 2 and command[1] == "-c" else None
        for index, argument in enumerate(command):
            if index == python_source_index or not isinstance(argument, str):
                continue
            if argument.startswith("@") and len(argument) > 1:
                candidates = [argument[1:]]
            elif argument.startswith("-") and "=" in argument:
                candidates = [argument.split("=", 1)[1]]
            else:
                candidates = [argument]
            for candidate in candidates:
                if "{artifact_dir}" in candidate or "{python}" in candidate:
                    continue
                candidate = candidate.replace("{root}\\", "").replace("{root}/", "")
                if not _safe_relative_path(candidate):
                    continue
                path = root / candidate
                if path.is_file() or any(mark in candidate for mark in ("/", "\\", ".")):
                    add_path(candidate)

    files = [
        {
            "path": raw,
            "sha256": sha256_file(root / raw),
            "bytes": (root / raw).stat().st_size,
        }
        for raw in sorted(selected)
    ]
    tree_payload = json.dumps(
        {"files": files, "missing": sorted(missing)},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "schema_version": "1.0",
        "algorithm": "sha256",
        "files": files,
        "missing": sorted(missing),
        "tree_sha256": hashlib.sha256(tree_payload).hexdigest(),
    }


def task_path(root: Path, task_id: str) -> Path:
    matches = list((root / "research" / "tasks").glob(f"{task_id}.json"))
    if len(matches) != 1:
        raise ProtocolError(f"unknown or ambiguous task id: {task_id}")
    return matches[0]


def load_task(root: Path, task_id: str) -> dict[str, Any]:
    task = read_json(task_path(root, task_id))
    validate_task(task, root=root)
    return task


def list_tasks(root: Path) -> list[dict[str, Any]]:
    tasks = []
    for path in sorted((root / "research" / "tasks").glob("T*.json")):
        task = read_json(path)
        validate_task(task, root=root)
        tasks.append(task)
    return tasks


def _safe_relative_path(raw: str) -> bool:
    if (
        not isinstance(raw, str)
        or raw.strip() == ""
        or any(ord(character) < 32 for character in raw)
        or ":" in raw
    ):
        return False
    path = PurePosixPath(raw.replace("\\", "/"))
    windows_path = PureWindowsPath(raw)
    unsafe_part = any(
        ":" in part
        or part[-1:] in {" ", "."}
        or any(ord(character) < 32 for character in part)
        for part in path.parts
    )
    return (
        bool(path.parts)
        and not path.is_absolute()
        and not windows_path.is_absolute()
        and not windows_path.drive
        and not windows_path.anchor
        and ".." not in path.parts
        and not windows_path.is_reserved()
        and not unsafe_part
    )


def validate_task(task: dict[str, Any], root: Path | None = None) -> None:
    required = {
        "schema_version",
        "task_id",
        "title",
        "role",
        "objective",
        "claim_ids",
        "dependencies",
        "inputs",
        "allowed_max_evidence",
        "required_artifacts",
        "acceptance_checks",
        "status",
    }
    missing = required - task.keys()
    if missing:
        raise ProtocolError(f"task missing fields: {sorted(missing)}")
    if task["schema_version"] != "1.0":
        raise ProtocolError("unsupported task schema version")
    if task["role"] not in ROLES:
        raise ProtocolError(f"unknown role: {task['role']}")
    if task["allowed_max_evidence"] not in EVIDENCE_RANK:
        raise ProtocolError("invalid allowed_max_evidence")
    research_mode = task.get("research_mode")
    if research_mode is not None and research_mode not in RESEARCH_MODES:
        raise ProtocolError(f"invalid research_mode: {research_mode}")
    dependency_mode = task.get("dependency_mode", "latest_validated_run")
    if not isinstance(dependency_mode, str) or dependency_mode not in DEPENDENCY_MODES:
        raise ProtocolError(f"invalid dependency_mode: {dependency_mode}")
    route_ids = task.get("route_ids", [])
    if not isinstance(route_ids, list) or len(route_ids) != len(set(route_ids)):
        raise ProtocolError("route_ids must be a unique array")
    for route_id in route_ids:
        if not isinstance(route_id, str) or not ROUTE_ID_PATTERN.fullmatch(route_id):
            raise ProtocolError(f"invalid route id: {route_id!r}")
    if research_mode == "continuation_depth" and len(route_ids) != 1:
        raise ProtocolError(
            "continuation_depth tasks must name exactly one active frontier route"
        )
    inputs = task.get("inputs")
    if not isinstance(inputs, list) or len(inputs) != len(set(inputs)):
        raise ProtocolError("inputs must be a unique array")
    for raw in inputs:
        if not isinstance(raw, str) or not _safe_relative_path(raw):
            raise ProtocolError(f"unsafe input path: {raw!r}")
    fanout_manifest = task.get("fanout_manifest")
    if fanout_manifest is not None and (
        not isinstance(fanout_manifest, str)
        or not _safe_relative_path(fanout_manifest)
    ):
        raise ProtocolError("fanout_manifest must be a safe repository-relative path")
    if fanout_manifest is not None:
        manifest_path = PurePosixPath(fanout_manifest.replace("\\", "/"))
        if (
            fanout_manifest != manifest_path.as_posix()
            or len(manifest_path.parts) != 3
            or manifest_path.parts[:2] != ("research", "fanouts")
            or manifest_path.suffix != ".json"
        ):
            raise ProtocolError(
                "fanout_manifest must be a canonical research/fanouts/*.json path"
            )
    context_policy = task.get("context_policy", {})
    if context_policy:
        if not isinstance(context_policy, dict):
            raise ProtocolError("context_policy must be an object")
        context_mode = context_policy.get("mode")
        if context_mode not in CONTEXT_MODES:
            raise ProtocolError(f"invalid context mode: {context_mode}")
        for field in ("allowlist", "denylist"):
            values = context_policy.get(field, [])
            if not isinstance(values, list) or len(values) != len(set(values)):
                raise ProtocolError(f"context_policy.{field} must be a unique array")
            for raw in values:
                if not isinstance(raw, str) or not _safe_relative_path(raw):
                    raise ProtocolError(f"unsafe context path in {field}: {raw!r}")
        if research_mode == "sealed_breadth" and context_mode == "full_history":
            raise ProtocolError("sealed_breadth tasks cannot use full_history context")
        if research_mode == "sealed_breadth" and not context_policy.get(
            "reveal_after_route_card", False
        ):
            raise ProtocolError(
                "sealed_breadth tasks must reveal declared history only after an immutable route card"
            )
        if context_policy.get("allowlist") and not set(context_policy["allowlist"]).issubset(
            set(task.get("inputs", []))
        ):
            raise ProtocolError("context_policy.allowlist must be a subset of task inputs")
    if research_mode == "sealed_breadth":
        rollout = task.get("rollout_strategy", {})
        if not isinstance(rollout, dict) or not rollout.get("immutable_route_card"):
            raise ProtocolError("sealed_breadth tasks require an immutable route-card strategy")
    method_constraints = task.get("method_constraints", {})
    if method_constraints and not isinstance(method_constraints, dict):
        raise ProtocolError("method_constraints must be an object")
    if not isinstance(task.get("may_refute_master_claim", False), bool):
        raise ProtocolError("may_refute_master_claim must be a boolean")
    if not isinstance(task.get("strict_claim_binding", False), bool):
        raise ProtocolError("strict_claim_binding must be a boolean")
    if not isinstance(task.get("require_distinct_dependency_workers", False), bool):
        raise ProtocolError("require_distinct_dependency_workers must be a boolean")
    dynamic_verifier_artifacts = task.get("dynamic_verifier_artifacts", [])
    if (
        not isinstance(dynamic_verifier_artifacts, list)
        or len(dynamic_verifier_artifacts) != len(set(dynamic_verifier_artifacts))
    ):
        raise ProtocolError("dynamic_verifier_artifacts must be a unique array")
    for raw in dynamic_verifier_artifacts:
        if not isinstance(raw, str) or not _safe_relative_path(raw):
            raise ProtocolError(f"unsafe dynamic verifier artifact path: {raw!r}")
        if PurePosixPath(raw.replace("\\", "/")).suffix.lower() != ".py":
            raise ProtocolError("dynamic verifier artifacts must be Python files")
        if raw not in task.get("required_artifacts", []):
            raise ProtocolError(
                "dynamic verifier artifacts must also be listed in required_artifacts"
            )
    verifiers = task.get("verifiers", [])
    if not isinstance(verifiers, list):
        raise ProtocolError("verifiers must be an array")
    verifier_names: set[str] = set()
    for verifier in verifiers:
        if not isinstance(verifier, dict):
            raise ProtocolError("each verifier must be an object")
        name = verifier.get("name")
        command = verifier.get("command")
        if not isinstance(name, str) or not name.strip() or name in verifier_names:
            raise ProtocolError(f"invalid or duplicate verifier name: {name!r}")
        verifier_names.add(name)
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            raise ProtocolError(f"verifier {name} command must be a non-empty argv array")
        from .verifiers import validate_verifier_spec

        verifier_errors = validate_verifier_spec(verifier)
        if verifier_errors:
            raise ProtocolError(
                f"invalid verifier {name!r}: " + "; ".join(verifier_errors)
            )
    if root is not None:
        resolved_root = root.resolve()
        for raw in inputs:
            candidate = (resolved_root / raw).resolve()
            try:
                candidate.relative_to(resolved_root)
            except (OSError, ValueError) as error:
                raise ProtocolError(f"task input escapes repository root: {raw}") from error
            if not candidate.exists():
                raise ProtocolError(f"task input does not exist: {raw}")
        if fanout_manifest is not None:
            candidate = (resolved_root / fanout_manifest).resolve()
            try:
                candidate.relative_to(resolved_root)
            except (OSError, ValueError) as error:
                raise ProtocolError("task fanout_manifest escapes repository root") from error
            if not candidate.is_file():
                raise ProtocolError(f"task fanout_manifest does not exist: {fanout_manifest}")
        for raw in context_policy.get("allowlist", []):
            if not (resolved_root / raw).exists():
                raise ProtocolError(f"context allowlist input does not exist: {raw}")
        if route_ids:
            from .routes import active_frontier_routes, load_route_nodes

            route_nodes = load_route_nodes(root)
            known_route_ids = {route.get("route_id") for route in route_nodes}
            unknown_route_ids = sorted(set(route_ids) - known_route_ids)
            if unknown_route_ids:
                raise ProtocolError(f"task references unknown route ids: {unknown_route_ids}")
            if research_mode == "continuation_depth" and task.get("status") == "ready":
                frontier_ids = {
                    route.get("route_id") for route in active_frontier_routes(route_nodes)
                }
                if route_ids[0] not in frontier_ids:
                    raise ProtocolError(
                        "continuation_depth task does not target a current active frontier route"
                    )


def unmet_task_dependencies(root: Path, task: dict[str, Any]) -> list[str]:
    """Return dependencies that do not satisfy the task's dependency mode."""

    unmet: list[str] = []
    dependency_mode = task.get("dependency_mode", "latest_validated_run")
    for dependency in task.get("dependencies", []):
        try:
            dependency_task = load_task(root, dependency)
        except ProtocolError:
            unmet.append(dependency)
            continue
        if dependency_mode == "complete_validated_fanout":
            if latest_completed_fanout(root, dependency) is None:
                unmet.append(dependency)
        elif latest_completed_run(root, dependency) is None:
            unmet.append(dependency)
    return unmet


def latest_completed_run(root: Path, task_id: str) -> Path | None:
    """Return the newest harness-validated completed run for ``task_id``.

    Task JSON is immutable coordination input. Completion belongs to a concrete
    run, so a downstream audit need not wait for a maintainer to rewrite the
    upstream task's status after every portable execution.
    """

    task_runs = root / "runs" / task_id
    if not task_runs.is_dir():
        return None
    candidates = (
        path for path in task_runs.iterdir() if path.is_dir() and path.name != "ensembles"
    )
    for run_dir in sorted(candidates, key=lambda path: path.name, reverse=True):
        invocation_path = run_dir / "invocation.json"
        if not invocation_path.is_file():
            continue
        try:
            invocation = read_json(invocation_path)
            strategy = invocation.get("rollout_strategy")
            if strategy is not None and not isinstance(strategy, dict):
                continue
            from .fanout import _validated_run_attestation

            _validated_run_attestation(
                root,
                task_id,
                strategy,
                run_dir,
            )
        except (KeyError, OSError, ProtocolError, ValueError):
            continue
        return run_dir
    return None


def _validated_fanout_result_paths(
    root: Path, task_id: str, ensemble_path: Path
) -> list[Path] | None:
    """Return every result in one complete ensemble, or reject it atomically.

    The ensemble is only an index.  Each referenced run remains authoritative,
    and all of its harness completion files must still attest success.  No
    subset is returned: one incomplete or unsafe rollout invalidates the whole
    ensemble for dependency purposes.
    """

    root = root.resolve()
    try:
        task = load_task(root, task_id)
    except ProtocolError:
        return None
    task_runs = (root / "runs" / task_id).resolve()
    ensemble_root = (task_runs / "ensembles").resolve()
    try:
        resolved_ensemble = ensemble_path.resolve()
        relative_ensemble = resolved_ensemble.relative_to(ensemble_root)
    except (OSError, ValueError):
        return None
    if len(relative_ensemble.parts) != 2 or relative_ensemble.name != "ensemble.json":
        return None
    try:
        ensemble = read_json(resolved_ensemble)
    except ProtocolError:
        return None
    if (
        ensemble.get("schema_version") != "1.0"
        or ensemble.get("kind") != "rpcd-independent-rollout-ensemble"
        or ensemble.get("ensemble_id") != relative_ensemble.parts[0]
        or ensemble.get("task_id") != task_id
        or ensemble.get("dry_run") is not False
        or ensemble.get("complete") is not True
    ):
        return None
    rollouts = ensemble.get("rollouts")
    if not isinstance(rollouts, list) or not rollouts:
        return None

    # A completed subset is not a complete fanout.  Authenticate the intended
    # rollout set against the repository-owned source manifest so deleting a
    # failed ensemble record cannot manufacture a satisfied dependency.
    raw_manifest = ensemble.get("source_manifest")
    manifest_hash = ensemble.get("source_manifest_sha256")
    if (
        not isinstance(raw_manifest, str)
        or not _safe_relative_path(raw_manifest)
        or not isinstance(manifest_hash, str)
    ):
        return None
    manifest_path = (root / raw_manifest).resolve()
    try:
        manifest_path.relative_to(root)
    except (OSError, ValueError):
        return None
    try:
        if not manifest_path.is_file() or sha256_file(manifest_path) != manifest_hash:
            return None
        manifest = read_json(manifest_path)
        from .fanout import (
            _require_task_fanout_manifest,
            _validated_run_attestation,
            validate_fanout_manifest,
        )

        if validate_fanout_manifest(manifest, task_id=task_id):
            return None
        _require_task_fanout_manifest(task, raw_manifest)
    except (OSError, ProtocolError):
        return None
    source_rollouts = manifest.get("rollouts")
    if not isinstance(source_rollouts, list):
        return None
    source_by_id = {
        rollout.get("rollout_id"): rollout
        for rollout in source_rollouts
        if isinstance(rollout, dict)
    }
    source_ids = [
        rollout.get("rollout_id")
        for rollout in source_rollouts
        if isinstance(rollout, dict)
    ]
    ensemble_ids = [
        rollout.get("rollout_id")
        for rollout in rollouts
        if isinstance(rollout, dict)
    ]
    if (
        len(source_by_id) != len(source_rollouts)
        or len(ensemble_ids) != len(rollouts)
        or not all(isinstance(rollout_id, str) for rollout_id in ensemble_ids)
        or len(set(ensemble_ids)) != len(ensemble_ids)
        or ensemble_ids != source_ids
        or ensemble.get("selected_rollout_ids") != source_ids
        or ensemble.get("distinct_method_families")
        != sorted({rollout.get("method_family") for rollout in source_rollouts})
    ):
        return None

    source_shards = ensemble.get("source_shards")
    if source_shards is None:
        if any(
            "source_shard" in rollout or "source_shard_sha256" in rollout
            for rollout in rollouts
        ):
            return None
    else:
        if not isinstance(source_shards, list) or not source_shards:
            return None
        shard_records: dict[str, tuple[str, dict[str, Any]]] = {}
        seen_shard_paths: set[str] = set()
        for entry in source_shards:
            if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
                return None
            raw_shard = entry.get("path")
            shard_hash = entry.get("sha256")
            if (
                not isinstance(raw_shard, str)
                or not _safe_relative_path(raw_shard)
                or not isinstance(shard_hash, str)
                or raw_shard in seen_shard_paths
            ):
                return None
            shard_path = (root / raw_shard).resolve()
            try:
                relative_shard = shard_path.relative_to(ensemble_root)
                canonical_shard = shard_path.relative_to(root).as_posix()
            except (OSError, ValueError):
                return None
            if (
                raw_shard != canonical_shard
                or len(relative_shard.parts) != 2
                or relative_shard.name != "ensemble.json"
                or shard_path == resolved_ensemble
                or not shard_path.is_file()
                or shard_path.is_symlink()
            ):
                return None
            try:
                if sha256_file(shard_path) != shard_hash:
                    return None
                shard = read_json(shard_path)
            except (OSError, ProtocolError):
                return None
            shard_rollouts = shard.get("rollouts")
            shard_ids = [
                record.get("rollout_id")
                for record in shard_rollouts
                if isinstance(record, dict)
            ] if isinstance(shard_rollouts, list) else []
            if (
                shard.get("schema_version") != "1.0"
                or shard.get("kind") != "rpcd-independent-rollout-ensemble"
                or shard.get("ensemble_id") != relative_shard.parts[0]
                or shard.get("task_id") != task_id
                or shard.get("dry_run") is not False
                or shard.get("complete") is not False
                or shard.get("source_manifest") != raw_manifest
                or shard.get("source_manifest_sha256") != manifest_hash
                or not shard_ids
                or len(shard_ids) != len(shard_rollouts)
                or len(shard_ids) != len(set(shard_ids))
                or shard.get("selected_rollout_ids") != shard_ids
            ):
                return None
            for record in shard_rollouts:
                rollout_id = record["rollout_id"]
                if rollout_id in shard_records:
                    return None
                shard_records[rollout_id] = (raw_shard, record)
            seen_shard_paths.add(raw_shard)
        if set(shard_records) != set(source_ids):
            return None
        for rollout in rollouts:
            rollout_id = rollout["rollout_id"]
            raw_shard, shard_record = shard_records[rollout_id]
            shard_hash = next(
                entry["sha256"] for entry in source_shards if entry["path"] == raw_shard
            )
            if (
                rollout.get("source_shard") != raw_shard
                or rollout.get("source_shard_sha256") != shard_hash
            ):
                return None
            base_record = dict(rollout)
            base_record.pop("source_shard", None)
            base_record.pop("source_shard_sha256", None)
            if base_record != shard_record:
                return None

    result_paths: list[Path] = []
    seen_run_dirs: set[Path] = set()
    for rollout in rollouts:
        if not isinstance(rollout, dict) or rollout.get("status") != "completed":
            return None
        source_rollout = source_by_id[rollout.get("rollout_id")]
        if any(
            rollout.get(field) != source_rollout.get(field)
            for field in ("worker", "method_family")
        ):
            return None
        raw_run_dir = rollout.get("run_dir")
        if not isinstance(raw_run_dir, str) or not _safe_relative_path(raw_run_dir):
            return None
        run_dir = (root / raw_run_dir).resolve()
        try:
            relative_run = run_dir.relative_to(task_runs)
        except (OSError, ValueError):
            return None
        # A dependency rollout must be one concrete run directly below its
        # task, never another task, an ensemble directory, or an escaped path.
        if len(relative_run.parts) != 1 or relative_run.name == "ensembles":
            return None
        if run_dir in seen_run_dirs:
            return None
        seen_run_dirs.add(run_dir)

        try:
            canonical_run_dir, _ = _validated_run_attestation(
                root,
                task_id,
                source_rollout,
                run_dir,
                recorded=rollout.get("run_attestation"),
            )
        except (KeyError, OSError, ProtocolError, ValueError):
            return None
        if canonical_run_dir != raw_run_dir:
            return None
        result_paths.append(run_dir / "result.json")
    return result_paths


def latest_completed_fanout(
    root: Path, task_id: str
) -> tuple[Path, list[Path]] | None:
    """Return the newest atomically complete, validated non-dry ensemble.

    Fanout IDs begin with a UTC timestamp, so the repository's ensemble
    directory names give the same portable newest-first ordering used for
    ordinary run IDs.  Invalid newer ensembles are skipped rather than allowed
    to shadow the newest complete ensemble.
    """

    ensemble_root = root / "runs" / task_id / "ensembles"
    if not ensemble_root.is_dir():
        return None
    candidates = sorted(
        ensemble_root.glob("*/ensemble.json"),
        key=lambda path: path.parent.name,
        reverse=True,
    )
    for ensemble_path in candidates:
        result_paths = _validated_fanout_result_paths(root, task_id, ensemble_path)
        if result_paths is not None:
            return ensemble_path.parent, result_paths
    return None


def dependency_result_paths(root: Path, task: dict[str, Any]) -> list[str]:
    """Return portable paths to validated dependency results."""

    paths: list[str] = []
    dependency_mode = task.get("dependency_mode", "latest_validated_run")
    for dependency in task.get("dependencies", []):
        if dependency_mode == "complete_validated_fanout":
            completed_fanout = latest_completed_fanout(root, dependency)
            if completed_fanout is not None:
                _, result_paths = completed_fanout
                paths.extend(path.relative_to(root).as_posix() for path in result_paths)
            continue
        run_dir = latest_completed_run(root, dependency)
        if run_dir is not None:
            paths.append((run_dir / "result.json").relative_to(root).as_posix())
    return paths


def _normalized_text(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def avenue_signature(avenue: dict[str, Any]) -> tuple[str, ...]:
    """Return a conservative exact signature used before semantic review.

    This deliberately catches exact/rephrased duplicates without pretending to
    solve mathematical equivalence.  The route DAG reviewer remains responsible
    for semantic clustering.
    """

    structured = (
        _normalized_text(avenue.get("method_family")),
        _normalized_text(avenue.get("representation")),
        _normalized_text(avenue.get("state_or_invariant")),
        _normalized_text(avenue.get("core_candidate_lemma")),
    )
    if any(structured):
        return structured
    return (
        _normalized_text(avenue.get("name")),
        _normalized_text(avenue.get("objective")),
    )


def validate_route_card(
    card: dict[str, Any],
    *,
    task: dict[str, Any],
    rollout_strategy: dict[str, Any] | None = None,
) -> list[str]:
    """Validate the immutable statement-first card for a sealed breadth run."""

    required = {
        "schema_version",
        "route_card_id",
        "task_id",
        "rollout_id",
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
    }
    errors: list[str] = []
    missing = required - card.keys()
    if missing:
        errors.append(f"route card missing fields: {sorted(missing)}")
        return errors
    extra = sorted(set(card) - required)
    if extra:
        errors.append(f"route card has unsupported fields: {extra}")
    if card.get("schema_version") != "1.0":
        errors.append("unsupported route card schema version")
    if card.get("task_id") != task.get("task_id"):
        errors.append("route card task_id does not match the assigned task")
    strategy = rollout_strategy or {}
    expected_rollout = strategy.get("rollout_id", task.get("task_id"))
    if card.get("rollout_id") != expected_rollout:
        errors.append("route card rollout_id does not match invocation lineage")
    expected_family = strategy.get("method_family") or task.get("method_constraints", {}).get(
        "method_family"
    )
    if expected_family and card.get("method_family") != expected_family:
        errors.append("route card method_family does not match the assigned strategy")
    expected_context = strategy.get("context_mode") or task.get("context_policy", {}).get("mode")
    if card.get("context_mode") != expected_context:
        errors.append("route card context_mode does not match the sealed context")
    expected_parents = strategy.get("route_ids") or task.get("route_ids", [])
    if expected_parents and set(card.get("parent_route_ids", [])) != set(expected_parents):
        errors.append("route card parent_route_ids do not match the assigned route lineage")
    for field in (
        "route_card_id",
        "method_family",
        "representation",
        "state_or_invariant",
        "core_candidate_lemma",
        "predicted_failure",
        "falsifier",
        "target_implication",
    ):
        if not isinstance(card.get(field), str) or not card[field].strip():
            errors.append(f"route card {field} must be a non-empty string")
    for field in ("information_retained", "information_discarded", "parent_route_ids"):
        value = card.get(field)
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            errors.append(f"route card {field} must be an array of non-empty strings")
        elif len(value) != len(set(value)):
            errors.append(f"route card {field} must not contain duplicates")
    for field in ("information_retained", "information_discarded"):
        if isinstance(card.get(field), list) and not card[field]:
            errors.append(f"route card {field} must not be empty")
    for route_id in card.get("parent_route_ids", []):
        if isinstance(route_id, str) and not ROUTE_ID_PATTERN.fullmatch(route_id):
            errors.append(f"route card has invalid parent route id: {route_id!r}")
    return errors


def validate_result(
    result: dict[str, Any],
    task: dict[str, Any] | None = None,
    *,
    root: Path | None = None,
    iteration_policy: dict[str, Any] | None = None,
    active_seconds: float | None = None,
    rollout_strategy: Mapping[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "task_id",
        "run_id",
        "worker",
        "status",
        "summary",
        "claims",
        "artifacts",
        "checks",
        "failed_attempts",
        "iteration",
        "literature",
        "next_tasks",
        "limitations",
    }
    missing = required - result.keys()
    if missing:
        errors.append(f"missing result fields: {sorted(missing)}")
        return errors
    if result["schema_version"] != "1.0":
        errors.append("unsupported result schema version")
    if result["status"] not in {"succeeded", "partial", "failed"}:
        errors.append(f"invalid run status: {result['status']}")
    if task is not None and result["task_id"] != task["task_id"]:
        errors.append("result task_id does not match assigned task")

    max_rank = EVIDENCE_RANK[task["allowed_max_evidence"]] if task else 6
    for index, claim in enumerate(result.get("claims", [])):
        prefix = f"claims[{index}]"
        level = claim.get("evidence_level")
        status = claim.get("status")
        if level not in EVIDENCE_RANK:
            errors.append(f"{prefix}: invalid evidence level {level}")
            continue
        if EVIDENCE_RANK[level] > max_rank:
            errors.append(f"{prefix}: {level} exceeds task ceiling E{max_rank}")
        if status not in RESULT_STATUSES:
            errors.append(f"{prefix}: invalid claim status {status}")
        if status == "theorem_candidate" and EVIDENCE_RANK[level] < 5:
            errors.append(f"{prefix}: theorem_candidate requires E5 or higher")
        if status == "refuted" and EVIDENCE_RANK[level] < 2:
            errors.append(f"{prefix}: refuted requires at least E2")
        if status == "finite_verified" and EVIDENCE_RANK[level] < 2:
            errors.append(f"{prefix}: finite_verified requires at least E2")
        if status == "numerical_observation" and EVIDENCE_RANK[level] > 2:
            errors.append(f"{prefix}: numerical observation cannot exceed E2")
        if task and task.get("strict_claim_scope") and claim.get("claim_id") not in task.get(
            "claim_ids", []
        ):
            errors.append(f"{prefix}: claim id is outside the assigned task scope")
        if task and task.get("strict_claim_binding"):
            claim_id = claim.get("claim_id")
            if root is None:
                errors.append(f"{prefix}: strict claim binding requires the repository root")
            elif not isinstance(claim_id, str):
                errors.append(f"{prefix}: strict claim binding requires a claim_id")
            else:
                matches = sorted((root / "research" / "claims").glob(f"{claim_id}-*.json"))
                if len(matches) != 1:
                    errors.append(
                        f"{prefix}: canonical claim registry lookup returned {len(matches)} records"
                    )
                else:
                    try:
                        canonical = read_json(matches[0])
                    except ProtocolError as error:
                        errors.append(f"{prefix}: cannot read canonical claim: {error}")
                    else:
                        if claim.get("statement") != canonical.get("title"):
                            errors.append(
                                f"{prefix}: statement must equal the canonical claim title; "
                                "route-local lemmas need their own route/subclaim identity"
                            )
                        if claim.get("statement_ref") != canonical.get("statement_ref"):
                            errors.append(
                                f"{prefix}: statement_ref does not match the canonical claim registry"
                            )
        if (
            task
            and status == "refuted"
            and claim.get("claim_id") in MASTER_CLAIM_IDS
            and not task.get("may_refute_master_claim", False)
        ):
            errors.append(
                f"{prefix}: this task may refute a route lemma, but is not authorized "
                "to mark a canonical master claim refuted"
            )

    for index, check in enumerate(result.get("checks", [])):
        if not isinstance(check, dict):
            errors.append(f"checks[{index}] must be an object")
        elif check.get("exit_code") != 0:
            errors.append(f"checks[{index}] did not pass (exit_code={check.get('exit_code')!r})")

    for index, artifact in enumerate(result.get("artifacts", [])):
        raw = artifact.get("path", "") if isinstance(artifact, dict) else ""
        if not _safe_relative_path(raw):
            errors.append(f"artifacts[{index}]: unsafe relative path {raw!r}")
    if task is not None:
        declared = {
            PurePosixPath(artifact.get("path", "").replace("\\", "/")).as_posix()
            for artifact in result.get("artifacts", [])
            if isinstance(artifact, dict) and artifact.get("path")
        }
        for required_artifact in task.get("required_artifacts", []):
            normalized = PurePosixPath(required_artifact.replace("\\", "/")).as_posix()
            if not any(path == normalized or path.endswith("/" + normalized) for path in declared):
                errors.append(f"missing required artifact declaration: {required_artifact}")

    iteration = result.get("iteration")
    if not isinstance(iteration, dict):
        errors.append("iteration must be an object")
    else:
        required_iteration = {"avenues", "checkpoints", "stress_tests", "deepest_obstruction"}
        missing_iteration = required_iteration - iteration.keys()
        if missing_iteration:
            errors.append(f"iteration missing fields: {sorted(missing_iteration)}")
        policy = iteration_policy or DEFAULT_ITERATION_POLICY
        avenues = iteration.get("avenues", [])
        checkpoints = iteration.get("checkpoints", [])
        stress_tests = iteration.get("stress_tests", [])
        if not isinstance(avenues, list):
            errors.append("iteration.avenues must be an array")
        research_mode = task.get("research_mode") if task is not None else None
        required_avenues = {
            "sealed_breadth": 1,
            "continuation_depth": 1,
            "critic_validation": 2,
        }.get(research_mode, policy["minimum_distinct_avenues"])
        if isinstance(avenues, list) and len(avenues) < required_avenues:
            errors.append(
                "iteration has too few distinct avenues: "
                f"{len(avenues)} < {required_avenues}"
            )
        if isinstance(avenues, list):
            for index, avenue in enumerate(avenues):
                if not isinstance(avenue, dict):
                    errors.append(f"avenues[{index}] must be an object")
                    continue
                for field in ("name", "objective", "outcome"):
                    value = avenue.get(field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"avenues[{index}] {field} must be a non-empty string"
                        )
                if "parent_route_ids" in avenue:
                    parents_value = avenue.get("parent_route_ids")
                    if not isinstance(parents_value, list) or not all(
                        isinstance(parent, str) and parent.strip()
                        for parent in parents_value
                    ):
                        errors.append(
                            f"avenues[{index}] parent_route_ids must be an array of non-empty strings"
                        )
                    elif len(parents_value) != len(set(parents_value)):
                        errors.append(
                            f"avenues[{index}] parent_route_ids must not contain duplicates"
                        )
            signatures = [
                avenue_signature(avenue)
                for avenue in avenues
                if isinstance(avenue, dict)
            ]
            if len(signatures) != len(set(signatures)):
                errors.append("iteration avenues contain duplicate mathematical signatures")
            if task is not None and research_mode == "sealed_breadth":
                required_fields = {
                    "method_family",
                    "representation",
                    "state_or_invariant",
                    "core_candidate_lemma",
                    "information_retained",
                    "information_discarded",
                    "target_implication",
                    "predicted_failure",
                    "falsifier",
                    "context_mode",
                    "parent_route_ids",
                }
                for index, avenue in enumerate(avenues):
                    if not isinstance(avenue, dict):
                        continue
                    missing_fields = [field for field in required_fields if not avenue.get(field)]
                    if missing_fields:
                        errors.append(
                            f"avenues[{index}] sealed route card fields missing: {sorted(missing_fields)}"
                        )
                    if avenue.get("context_mode") != task.get("context_policy", {}).get("mode"):
                        errors.append(f"avenues[{index}] context_mode does not match the task")
                assigned_family = (
                    rollout_strategy.get("method_family")
                    if isinstance(rollout_strategy, Mapping)
                    else task.get("method_constraints", {}).get("method_family")
                )
                if assigned_family and not any(
                    avenue.get("method_family") == assigned_family
                    for avenue in avenues
                    if isinstance(avenue, dict)
                ):
                    errors.append("sealed route does not use its assigned method_family")
            if task is not None and research_mode == "continuation_depth":
                required_fields = {
                    "route_id",
                    "parent_route_ids",
                    "first_bad_edge",
                    "source_layer",
                    "next_layer",
                    "branch_kind",
                    "core_candidate_lemma",
                    "predicted_failure",
                    "falsifier",
                    "decision",
                }
                assigned_routes = set(task.get("route_ids", []))
                linked_to_assigned_route = False
                bottleneck_reported = False
                branch_kinds: set[str] = set()
                for index, avenue in enumerate(avenues):
                    if not isinstance(avenue, dict):
                        continue
                    missing_fields = [field for field in required_fields if not avenue.get(field)]
                    if missing_fields:
                        errors.append(
                            f"avenues[{index}] depth-route fields missing: {sorted(missing_fields)}"
                        )
                    parents_value = avenue.get("parent_route_ids")
                    parents = (
                        set(parents_value) if isinstance(parents_value, list) else set()
                    )
                    source_layer = avenue.get("source_layer")
                    next_layer = avenue.get("next_layer")
                    adjacent_layers = {
                        "L0": "L1",
                        "L1": "L2",
                        "L2": "L3",
                        "L3": "L4",
                    }
                    if source_layer in adjacent_layers and next_layer != adjacent_layers[source_layer]:
                        errors.append(
                            f"avenues[{index}] next_layer is not immediately below source_layer"
                        )
                    if avenue.get("route_id") in parents:
                        errors.append(f"avenues[{index}] route_id cannot equal its parent route")
                    if parents & assigned_routes:
                        linked_to_assigned_route = True
                    if avenue.get("branch_kind") in {"repair", "attack"}:
                        branch_kinds.add(avenue["branch_kind"])
                    if avenue.get("status") in {"blocked", "refuted"} or avenue.get(
                        "decision"
                    ) in {"branch", "suspend", "prune"}:
                        bottleneck_reported = True
                if assigned_routes and not linked_to_assigned_route:
                    errors.append("continuation result is not linked to an assigned route node")
                if bottleneck_reported and not {"repair", "attack"}.issubset(branch_kinds):
                    errors.append(
                        "a blocked/refuted depth edge must branch into distinct repair and attack children"
                    )
                if root is not None and len(assigned_routes) == 1:
                    from .routes import load_route_nodes, validate_continuation_avenue

                    route_nodes = load_route_nodes(root)
                    assigned_route = next(iter(assigned_routes))
                    for index, avenue in enumerate(avenues):
                        if not isinstance(avenue, dict):
                            continue
                        for route_error in validate_continuation_avenue(
                            route_nodes, assigned_route, avenue
                        ):
                            errors.append(f"avenues[{index}]: {route_error}")
            if task is not None and research_mode == "critic_validation":
                required_fields = {
                    "representation",
                    "first_bad_edge",
                    "predicted_failure",
                    "falsifier",
                    "decision",
                }
                for index, avenue in enumerate(avenues):
                    if not isinstance(avenue, dict):
                        continue
                    missing_fields = [field for field in required_fields if not avenue.get(field)]
                    if missing_fields:
                        errors.append(
                            f"avenues[{index}] critic-route fields missing: {sorted(missing_fields)}"
                        )
        if not isinstance(checkpoints, list):
            errors.append("iteration.checkpoints must be an array")
        else:
            for index, checkpoint in enumerate(checkpoints):
                if not isinstance(checkpoint, dict):
                    errors.append(f"checkpoints[{index}] must be an object")
                    continue
                elapsed = checkpoint.get("elapsed_active_minutes")
                if (
                    not isinstance(elapsed, (int, float))
                    or isinstance(elapsed, bool)
                    or elapsed < 0
                ):
                    errors.append(
                        f"checkpoints[{index}] elapsed_active_minutes must be a non-negative number"
                    )
                for field in ("summary", "next_action"):
                    value = checkpoint.get(field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"checkpoints[{index}] {field} must be a non-empty string"
                        )
        if not isinstance(stress_tests, list):
            errors.append("iteration.stress_tests must be an array")
        elif len(result.get("failed_attempts", [])) + len(stress_tests) < policy[
            "minimum_failed_or_stress_tests"
        ]:
            errors.append("iteration has too few failed attempts or adversarial stress tests")

        if active_seconds is not None:
            minimum_seconds = 60.0 * policy["minimum_active_minutes_per_worker"]
            if active_seconds + 1e-6 < minimum_seconds:
                errors.append(
                    "active research time is below the iteration floor: "
                    f"{active_seconds / 60.0:.2f} < "
                    f"{policy['minimum_active_minutes_per_worker']} minutes"
                )
            expected_checkpoints = max(
                1,
                int(active_seconds // (60.0 * policy["checkpoint_interval_minutes"])),
            )
            if isinstance(checkpoints, list) and len(checkpoints) < expected_checkpoints:
                errors.append(
                    "iteration has too few substantive checkpoints for its active duration: "
                    f"{len(checkpoints)} < {expected_checkpoints}"
                )
    return errors


def claim_task(root: Path, task_id: str, worker: str, hours: int = 24) -> Path:
    if not worker.strip():
        raise ProtocolError("worker label cannot be empty")
    load_task(root, task_id)
    claim_path = root / "research" / "claims" / "active" / f"{task_id}.json"
    now = datetime.now(timezone.utc)
    if claim_path.exists():
        existing = read_json(claim_path)
        try:
            expires = datetime.fromisoformat(existing["expires_at"].replace("Z", "+00:00"))
        except (KeyError, ValueError) as error:
            raise ProtocolError(f"malformed existing claim: {claim_path}") from error
        if expires > now and existing.get("worker") != worker:
            raise ProtocolError(
                f"task is claimed by {existing.get('worker')} until {existing.get('expires_at')}"
            )
    claim = {
        "schema_version": "1.0",
        "task_id": task_id,
        "worker": worker,
        "claimed_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": (now + timedelta(hours=hours)).isoformat().replace("+00:00", "Z"),
        "advisory_only": True,
    }
    write_json(claim_path, claim)
    return claim_path


def checkpoint_run(root: Path, task_id: str, run_dir: Path) -> Path:
    task = load_task(root, task_id)
    root = root.resolve()
    resolved_run = run_dir.resolve()
    try:
        relative_run = resolved_run.relative_to(root)
    except ValueError as error:
        raise ProtocolError("run directory must be inside the repository") from error
    if not resolved_run.is_dir():
        raise ProtocolError(f"run directory does not exist: {run_dir}")
    expected_parent = (root / "runs" / task_id).resolve()
    if resolved_run.parent != expected_parent:
        raise ProtocolError(
            f"run directory must be a direct child of runs/{task_id}"
        )
    if resolved_run.is_symlink() or expected_parent.is_symlink():
        raise ProtocolError("checkpoint source directories cannot be symbolic links")
    invocation_path = resolved_run / "invocation.json"
    task_snapshot_path = resolved_run / "task.json"
    if not invocation_path.is_file() or not task_snapshot_path.is_file():
        raise ProtocolError("checkpoint source run must contain invocation.json and task.json")
    invocation = read_json(invocation_path)
    task_snapshot = read_json(task_snapshot_path)
    if (
        invocation.get("task_id") != task_id
        or invocation.get("run_id") != resolved_run.name
    ):
        raise ProtocolError("checkpoint source invocation identity does not match its run path")
    if task_snapshot != task:
        raise ProtocolError("checkpoint source task snapshot does not match the current task")
    entries = []
    for path in sorted(resolved_run.rglob("*")):
        if path.is_symlink():
            raise ProtocolError(
                f"checkpoint source run cannot contain symbolic links: {path}"
            )
        if path.is_file():
            entries.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                }
            )
    run_id = resolved_run.name
    checkpoint = {
        "schema_version": "1.0",
        "task_id": task["task_id"],
        "run_id": run_id,
        "run_dir": relative_run.as_posix(),
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_invocation_sha256": sha256_file(invocation_path),
        "task_snapshot_sha256": sha256_file(task_snapshot_path),
        "source_iteration_complete": invocation.get("iteration_complete") is True,
        "files": entries,
    }
    output = root / "research" / "checkpoints" / f"{task_id}--{run_id}.json"
    write_json(output, checkpoint)
    return output


def load_resume_checkpoint(
    root: Path,
    task_id: str,
    checkpoint_path: Path,
) -> dict[str, Any]:
    """Verify and resolve a portable checkpoint for a new continuation run.

    A resume is intentionally a *new* run. This authenticates only the
    inherited scientific state; source active-time credit and independent-
    breadth identity are never returned as credit for the new invocation.
    """

    root = root.resolve()
    task = load_task(root, task_id)
    unresolved_checkpoint = (
        checkpoint_path if checkpoint_path.is_absolute() else root / checkpoint_path
    )
    if unresolved_checkpoint.is_symlink():
        raise ProtocolError("resume checkpoint cannot be a symbolic link")
    resolved_checkpoint = unresolved_checkpoint.resolve()
    try:
        checkpoint_relative = resolved_checkpoint.relative_to(root)
    except ValueError as error:
        raise ProtocolError("resume checkpoint must be inside the repository") from error
    if not resolved_checkpoint.is_file():
        raise ProtocolError(f"resume checkpoint does not exist: {checkpoint_path}")
    checkpoint = read_json(resolved_checkpoint)
    if checkpoint.get("schema_version") != "1.0":
        raise ProtocolError("unsupported resume checkpoint schema version")
    required_checkpoint_fields = {
        "schema_version",
        "task_id",
        "run_id",
        "run_dir",
        "created_at",
        "source_invocation_sha256",
        "task_snapshot_sha256",
        "source_iteration_complete",
        "files",
    }
    missing_checkpoint_fields = required_checkpoint_fields - checkpoint.keys()
    if missing_checkpoint_fields:
        raise ProtocolError(
            "resume checkpoint is missing attestation fields: "
            + ", ".join(sorted(missing_checkpoint_fields))
        )
    created_at = checkpoint.get("created_at")
    if not isinstance(created_at, str):
        raise ProtocolError("resume checkpoint created_at must be an ISO-8601 timestamp")
    try:
        parsed_created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ProtocolError(
            "resume checkpoint created_at must be an ISO-8601 timestamp"
        ) from error
    if parsed_created_at.tzinfo is None:
        raise ProtocolError("resume checkpoint created_at must include a timezone")
    if checkpoint.get("task_id") != task_id:
        raise ProtocolError("resume checkpoint task_id does not match the requested task")
    run_id = checkpoint.get("run_id")
    if (
        not isinstance(run_id, str)
        or not run_id.strip()
        or Path(run_id).name != run_id
        or "/" in run_id
        or "\\" in run_id
    ):
        raise ProtocolError("resume checkpoint has an unsafe source run_id")
    expected_run_relative = PurePosixPath("runs", task_id, run_id).as_posix()
    if checkpoint.get("run_dir") != expected_run_relative:
        raise ProtocolError(
            "resume checkpoint run_dir is not the canonical run for its task/run identity"
        )
    source_run = (root / expected_run_relative).resolve()
    expected_parent = (root / "runs" / task_id).resolve()
    if source_run.parent != expected_parent or not source_run.is_dir():
        raise ProtocolError("resume checkpoint source run is missing or outside its task")
    if source_run.is_symlink() or expected_parent.is_symlink():
        raise ProtocolError("resume checkpoint source directories cannot be symbolic links")

    raw_entries = checkpoint.get("files")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ProtocolError("resume checkpoint files must be a nonempty array")
    entries: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes"}:
            raise ProtocolError(
                f"resume checkpoint files[{index}] must contain exactly path/sha256/bytes"
            )
        raw_path = entry.get("path")
        digest = entry.get("sha256")
        byte_count = entry.get("bytes")
        if (
            not isinstance(raw_path, str)
            or not _safe_relative_path(raw_path)
            or PurePosixPath(raw_path.replace("\\", "/")).as_posix() != raw_path
        ):
            raise ProtocolError(f"resume checkpoint files[{index}] has an unsafe path")
        if raw_path in entries:
            raise ProtocolError(f"resume checkpoint repeats file path: {raw_path}")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ProtocolError(
                f"resume checkpoint files[{index}] has an invalid SHA-256"
            )
        if (
            not isinstance(byte_count, int)
            or isinstance(byte_count, bool)
            or byte_count < 0
        ):
            raise ProtocolError(
                f"resume checkpoint files[{index}] has an invalid byte count"
            )
        candidate = root / raw_path
        if candidate.is_symlink():
            raise ProtocolError(f"resume checkpoint file cannot be a symbolic link: {raw_path}")
        resolved_candidate = candidate.resolve()
        try:
            resolved_candidate.relative_to(source_run)
        except ValueError as error:
            raise ProtocolError(
                f"resume checkpoint file is outside the source run: {raw_path}"
            ) from error
        if not resolved_candidate.is_file():
            raise ProtocolError(f"resume checkpoint file is missing: {raw_path}")
        if resolved_candidate.stat().st_size != byte_count:
            raise ProtocolError(f"resume checkpoint byte count changed: {raw_path}")
        if sha256_file(resolved_candidate) != digest:
            raise ProtocolError(f"resume checkpoint SHA-256 mismatch: {raw_path}")
        entries[raw_path] = entry

    actual_paths: set[str] = set()
    for candidate in sorted(source_run.rglob("*")):
        if candidate.is_symlink():
            raise ProtocolError(
                f"resume checkpoint source run contains a symbolic link: {candidate}"
            )
        if candidate.is_file():
            actual_paths.add(candidate.relative_to(root).as_posix())
    if set(entries) != actual_paths:
        missing_from_checkpoint = sorted(actual_paths - set(entries))
        missing_from_run = sorted(set(entries) - actual_paths)
        details = []
        if missing_from_checkpoint:
            details.append("unhashed current files=" + ",".join(missing_from_checkpoint))
        if missing_from_run:
            details.append("missing hashed files=" + ",".join(missing_from_run))
        raise ProtocolError(
            "resume checkpoint does not exactly cover the source run: " + "; ".join(details)
        )

    invocation_path = source_run / "invocation.json"
    task_snapshot_path = source_run / "task.json"
    for required_path, label in (
        (invocation_path, "invocation.json"),
        (task_snapshot_path, "task.json"),
    ):
        raw = required_path.relative_to(root).as_posix()
        if raw not in entries:
            raise ProtocolError(f"resume checkpoint does not hash source {label}")
    invocation_hash = sha256_file(invocation_path)
    task_snapshot_hash = sha256_file(task_snapshot_path)
    recorded_invocation_hash = checkpoint.get("source_invocation_sha256")
    if recorded_invocation_hash != invocation_hash:
        raise ProtocolError("resume checkpoint source_invocation_sha256 is inconsistent")
    recorded_task_hash = checkpoint.get("task_snapshot_sha256")
    if recorded_task_hash != task_snapshot_hash:
        raise ProtocolError("resume checkpoint task_snapshot_sha256 is inconsistent")

    invocation = read_json(invocation_path)
    task_snapshot = read_json(task_snapshot_path)
    if invocation.get("schema_version") != "1.0":
        raise ProtocolError("resume source invocation has an unsupported schema version")
    if invocation.get("task_id") != task_id or invocation.get("run_id") != run_id:
        raise ProtocolError("resume source invocation identity does not match its run path")
    if invocation.get("dry_run") is not False:
        raise ProtocolError("dry runs cannot be resumed from checkpoints")
    if invocation.get("iteration_complete") is True:
        raise ProtocolError("completed runs cannot be resumed from checkpoints")
    if invocation.get("iteration_complete") is not False:
        raise ProtocolError("resume source invocation is not marked as an incomplete run")
    if checkpoint.get("source_iteration_complete") is not False:
        raise ProtocolError("resume checkpoint does not attest an incomplete source run")
    final_validation_path = source_run / "validation.json"
    if final_validation_path.is_file():
        final_validation = read_json(final_validation_path)
        if final_validation.get("valid") is True:
            raise ProtocolError("a successfully validated final run cannot be resumed")
    if task_snapshot != task:
        raise ProtocolError("resume source task snapshot does not match the current task")
    current_source_snapshot = repository_source_snapshot(root, task)
    if invocation.get("repository_source_snapshot") != current_source_snapshot:
        raise ProtocolError(
            "resume source repository snapshot does not match the current checkout"
        )

    phases = invocation.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ProtocolError("resume source has no completed research phase to continue")
    source_artifact_dir = source_run / "artifacts"
    running_seconds = 0.0
    previous_result: Path | None = None
    previous_validation: Path | None = None
    previous_phase: dict[str, Any] | None = None
    for index, phase in enumerate(phases, start=1):
        if not isinstance(phase, dict) or phase.get("phase") != index:
            raise ProtocolError("resume source phase records are not contiguous")
        seconds = phase.get("active_seconds")
        cumulative = phase.get("cumulative_active_seconds")
        if (
            not isinstance(seconds, (int, float))
            or isinstance(seconds, bool)
            or not math.isfinite(float(seconds))
            or float(seconds) < 0.0
        ):
            raise ProtocolError(f"resume source phase {index} has invalid active_seconds")
        running_seconds += float(seconds)
        if (
            not isinstance(cumulative, (int, float))
            or isinstance(cumulative, bool)
            or not math.isfinite(float(cumulative))
            or not math.isclose(
                float(cumulative), running_seconds, rel_tol=1e-12, abs_tol=1e-6
            )
        ):
            raise ProtocolError(
                f"resume source phase {index} has inconsistent cumulative active time"
            )
        for field in ("prompt", "result", "events", "stderr"):
            raw = phase.get(field)
            if not isinstance(raw, str) or not _safe_relative_path(raw):
                raise ProtocolError(f"resume source phase {index} has unsafe {field} path")
            resolved = (root / raw).resolve()
            try:
                resolved.relative_to(source_run)
            except ValueError as error:
                raise ProtocolError(
                    f"resume source phase {index} {field} is outside its run"
                ) from error
        if phase.get("exit_code") != 0:
            continue
        expected_result = source_run / f"phase-{index:03d}-result.json"
        if (root / phase["result"]).resolve() != expected_result:
            raise ProtocolError(
                f"resume source phase {index} result path is noncanonical"
            )
        validation_path = source_run / f"phase-{index:03d}-validation.json"
        if not expected_result.is_file() or not validation_path.is_file():
            continue
        validation = read_json(validation_path)
        if not isinstance(validation.get("valid"), bool) or not isinstance(
            validation.get("errors"), list
        ):
            raise ProtocolError(
                f"resume source phase {index} has a malformed validation record"
            )
        result = read_json(expected_result)
        if (
            result.get("task_id") != task_id
            or result.get("run_id") != run_id
            or result.get("worker") != invocation.get("worker")
        ):
            raise ProtocolError(
                f"resume source phase {index} result identity is inconsistent"
            )
        result_artifacts = result.get("artifacts")
        if not isinstance(result_artifacts, list):
            raise ProtocolError(
                f"resume source phase {index} result has a malformed artifacts array"
            )
        for artifact_index, artifact in enumerate(result_artifacts):
            raw_artifact = artifact.get("path") if isinstance(artifact, dict) else None
            if not isinstance(raw_artifact, str) or not _safe_relative_path(raw_artifact):
                raise ProtocolError(
                    f"resume source phase {index} artifact {artifact_index} has an unsafe path"
                )
            resolved_artifact = (root / raw_artifact).resolve()
            try:
                resolved_artifact.relative_to(source_artifact_dir)
            except ValueError as error:
                raise ProtocolError(
                    f"resume source phase {index} artifact {artifact_index} is outside "
                    "the source artifact directory"
                ) from error
            if not resolved_artifact.exists() or resolved_artifact.is_symlink():
                raise ProtocolError(
                    f"resume source phase {index} artifact {artifact_index} is missing or linked"
                )
        previous_result = expected_result
        previous_validation = validation_path
        previous_phase = phase
    source_active_seconds = invocation.get("active_research_seconds")
    if (
        not isinstance(source_active_seconds, (int, float))
        or isinstance(source_active_seconds, bool)
        or not math.isfinite(float(source_active_seconds))
        or not math.isclose(
            float(source_active_seconds), running_seconds, rel_tol=1e-12, abs_tol=1e-6
        )
    ):
        raise ProtocolError("resume source invocation has inconsistent active research time")
    if previous_result is None or previous_validation is None or previous_phase is None:
        raise ProtocolError("resume source has no complete phase result/validation pair")

    inherited_artifacts: list[dict[str, Any]] = []
    artifact_root = PurePosixPath(source_artifact_dir.relative_to(root).as_posix())
    artifact_prefix = artifact_root.as_posix() + "/"
    for raw, entry in sorted(entries.items()):
        if raw.startswith(artifact_prefix):
            inherited_artifacts.append(
                {
                    "source_path": raw,
                    "relative_path": PurePosixPath(raw).relative_to(artifact_root).as_posix(),
                    "sha256": entry["sha256"],
                    "bytes": entry["bytes"],
                }
            )

    source_strategy = invocation.get("rollout_strategy")
    if source_strategy is not None and not isinstance(source_strategy, dict):
        raise ProtocolError("resume source rollout_strategy is malformed")
    source_resume = invocation.get("resume_lineage")
    if source_resume is not None:
        if (
            not isinstance(source_resume, dict)
            or source_resume.get("independence") is not False
            or source_resume.get("eligible_for_fanout") is not False
            or source_resume.get("counts_as_new_breadth") is not False
        ):
            raise ProtocolError("resume source has malformed continuation lineage")
        source_strategy = source_resume.get("validation_rollout_strategy")
        if source_strategy is not None and not isinstance(source_strategy, dict):
            raise ProtocolError("resume source inherited rollout strategy is malformed")

    route_card_path: Path | None = None
    route_card_sha256: str | None = None
    if task.get("research_mode") == "sealed_breadth":
        route_card_record = invocation.get("route_card")
        if not isinstance(route_card_record, Mapping):
            raise ProtocolError(
                "sealed breadth can resume only after its route card has been locked"
            )
        raw_card_path = route_card_record.get("path")
        if not isinstance(raw_card_path, str) or not _safe_relative_path(raw_card_path):
            raise ProtocolError("resume source route_card.path is unsafe")
        route_card_path = (root / raw_card_path).resolve()
        try:
            route_card_path.relative_to(source_artifact_dir)
        except ValueError as error:
            raise ProtocolError("resume source route card is outside its artifact directory") from error
        if route_card_path != source_artifact_dir / "route_card.json":
            raise ProtocolError("resume source locked route card path is noncanonical")
        if not route_card_path.is_file():
            raise ProtocolError("resume source locked route card is missing")
        route_card_sha256 = sha256_file(route_card_path)
        if (
            route_card_record.get("sha256") != route_card_sha256
            or invocation.get("route_card_sha256") != route_card_sha256
        ):
            raise ProtocolError("resume source locked route-card hash is inconsistent")
        card_errors = validate_route_card(
            read_json(route_card_path), task=task, rollout_strategy=source_strategy
        )
        if card_errors:
            raise ProtocolError(
                "resume source locked route card no longer validates: " + "; ".join(card_errors)
            )
        if source_resume is None:
            sealed_phases = [
                phase
                for phase in phases
                if phase.get("phase_kind") == "sealed_route_card"
            ]
            if len(sealed_phases) != 1:
                raise ProtocolError(
                    "sealed breadth checkpoint must attest exactly one locked route-card phase"
                )
            sealed_validation = read_json(
                source_run / f"phase-{sealed_phases[0]['phase']:03d}-validation.json"
            )
            if sealed_validation.get("valid") is not True:
                raise ProtocolError("resume source sealed route-card phase was not valid")

    return {
        "checkpoint": checkpoint,
        "checkpoint_path": resolved_checkpoint,
        "checkpoint_relative": checkpoint_relative.as_posix(),
        "checkpoint_sha256": sha256_file(resolved_checkpoint),
        "source_run": source_run,
        "source_run_relative": expected_run_relative,
        "source_invocation": invocation,
        "source_invocation_sha256": invocation_hash,
        "source_task_snapshot_sha256": task_snapshot_hash,
        "previous_result": previous_result,
        "previous_result_sha256": sha256_file(previous_result),
        "previous_validation": previous_validation,
        "previous_validation_sha256": sha256_file(previous_validation),
        "previous_phase": previous_phase,
        "source_active_research_seconds": float(source_active_seconds),
        "inherited_artifacts": inherited_artifacts,
        "route_card_path": route_card_path,
        "route_card_sha256": route_card_sha256,
        "validation_rollout_strategy": source_strategy,
    }


def audit_claim_ledger(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "research" / "claims").glob("C*.json")):
        claim = read_json(path)
        label = claim.get("claim_id", path.stem)
        level = claim.get("evidence_level")
        status = claim.get("status")
        gates = claim.get("gates", {})
        if level not in EVIDENCE_RANK:
            errors.append(f"{label}: invalid evidence level {level}")
            continue
        rank = EVIDENCE_RANK[level]
        supporting = claim.get("supporting_artifacts", [])
        if supporting is not None:
            if not isinstance(supporting, list) or not all(
                isinstance(raw, str) and _safe_relative_path(raw) for raw in supporting
            ):
                errors.append(f"{label}: supporting_artifacts must be safe repository paths")
            else:
                for raw in supporting:
                    if not (root / raw).exists():
                        errors.append(f"{label}: supporting artifact does not exist: {raw}")
        if status == "proof_candidate":
            if rank >= 3 and not gates.get("proof_draft"):
                errors.append(f"{label}: E3+ proof_candidate lacks proof_draft gate")
            if rank >= 4 and not gates.get("hostile_audit"):
                errors.append(f"{label}: E4+ proof_candidate lacks hostile_audit gate")
            if rank >= 5 and not gates.get("independent_reconstruction"):
                errors.append(f"{label}: E5+ proof_candidate lacks independent reconstruction")
            if rank >= 6 and not (
                gates.get("formalization") or gates.get("formal_or_human_validation")
            ):
                errors.append(f"{label}: E6 proof_candidate lacks formal or human validation")
        if status == "theorem_candidate":
            required_gates = [
                "finite_statement",
                "quantifiers_explicit",
                "domain_expert_spec_review",
                "proof_draft",
                "hostile_audit",
                "independent_reconstruction",
                "priority_audit",
            ]
            missing = [gate for gate in required_gates if not gates.get(gate)]
            if rank < 5:
                errors.append(f"{label}: theorem_candidate must be at least E5")
            if missing:
                errors.append(f"{label}: theorem_candidate missing gates {missing}")
            gate_evidence = claim.get("gate_evidence", {})
            if not isinstance(gate_evidence, dict):
                errors.append(f"{label}: theorem_candidate gate_evidence must be an object")
            else:
                workers: dict[str, str] = {}
                run_ids: dict[str, str] = {}
                for gate in required_gates:
                    evidence = gate_evidence.get(gate)
                    if not isinstance(evidence, dict):
                        errors.append(f"{label}: theorem_candidate lacks gate_evidence.{gate}")
                        continue
                    worker = evidence.get("worker")
                    run_id = evidence.get("run_id")
                    artifacts = evidence.get("artifacts")
                    if not isinstance(worker, str) or not worker.strip():
                        errors.append(f"{label}: gate_evidence.{gate}.worker is missing")
                    else:
                        workers[gate] = worker
                    if not isinstance(run_id, str) or not run_id.strip():
                        errors.append(f"{label}: gate_evidence.{gate}.run_id is missing")
                    else:
                        run_ids[gate] = run_id
                    raw_invocation = evidence.get("invocation")
                    if not isinstance(raw_invocation, str) or not _safe_relative_path(
                        raw_invocation
                    ):
                        errors.append(
                            f"{label}: gate_evidence.{gate}.invocation is missing or unsafe"
                        )
                    elif not (root / raw_invocation).is_file():
                        errors.append(
                            f"{label}: gate_evidence.{gate}.invocation does not exist"
                        )
                    else:
                        try:
                            invocation = read_json(root / raw_invocation)
                        except ProtocolError as error:
                            errors.append(f"{label}: gate_evidence.{gate}: {error}")
                        else:
                            if invocation.get("run_id") != run_id:
                                errors.append(
                                    f"{label}: gate_evidence.{gate} run_id is not owned by its invocation"
                                )
                            if invocation.get("worker") != worker:
                                errors.append(
                                    f"{label}: gate_evidence.{gate} worker is not owned by its invocation"
                                )
                            if invocation.get("iteration_complete") is not True:
                                errors.append(
                                    f"{label}: gate_evidence.{gate} invocation is not complete"
                                )
                    if not isinstance(artifacts, list) or not artifacts:
                        errors.append(f"{label}: gate_evidence.{gate}.artifacts is empty")
                    elif not all(
                        isinstance(raw, str)
                        and _safe_relative_path(raw)
                        and (root / raw).exists()
                        for raw in artifacts
                    ):
                        errors.append(
                            f"{label}: gate_evidence.{gate}.artifacts contains a missing or unsafe path"
                        )
                proof_chain = ("proof_draft", "hostile_audit", "independent_reconstruction")
                proof_workers = {workers.get(gate) for gate in proof_chain} - {None}
                proof_runs = {run_ids.get(gate) for gate in proof_chain} - {None}
                if len(proof_workers) < len(proof_chain):
                    errors.append(
                        f"{label}: proof, hostile audit, and reconstruction need distinct workers"
                    )
                if len(proof_runs) < len(proof_chain):
                    errors.append(
                        f"{label}: proof, hostile audit, and reconstruction need distinct runs"
                    )
                if (
                    workers.get("domain_expert_spec_review")
                    and workers.get("proof_draft")
                    and workers["domain_expert_spec_review"] == workers["proof_draft"]
                ):
                    errors.append(
                        f"{label}: domain specification review must be independent of the proof worker"
                    )
                if (
                    workers.get("priority_audit")
                    and workers.get("proof_draft")
                    and workers["priority_audit"] == workers["proof_draft"]
                ):
                    errors.append(
                        f"{label}: priority/novelty audit must be independent of the proof worker"
                    )
                if (
                    run_ids.get("priority_audit")
                    and run_ids.get("proof_draft")
                    and run_ids["priority_audit"] == run_ids["proof_draft"]
                ):
                    errors.append(
                        f"{label}: priority/novelty audit must use a different run from the proof"
                    )
        if status == "external_theorem" and claim.get("origin", {}).get("kind") != "external_theorem":
            errors.append(f"{label}: external theorem lacks an external_theorem origin")
    return errors
