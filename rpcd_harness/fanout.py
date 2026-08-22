"""Independent-rollout orchestration for breadth-first RPCD research."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable

from .protocol import (
    ProtocolError,
    load_iteration_policy,
    load_task,
    read_json,
    repository_source_snapshot,
    sha256_file,
    write_json,
)


CONTEXT_MODES = {"statement_only", "declared_inputs", "full_history"}
_ROLLOUT_FIELDS = {
    "rollout_id",
    "worker",
    "method_family",
    "context_mode",
    "route_ids",
    "objective",
    "forbidden_methods",
    "required_controls",
}

_RUN_ATTESTATION_FILES = {
    "invocation_sha256": "invocation.json",
    "task_sha256": "task.json",
    "validation_sha256": "validation.json",
    "result_sha256": "result.json",
    "artifact_manifest_sha256": "artifact_manifest.json",
    "trusted_preflight_sha256": "trusted_verifiers.preflight.json",
    "trusted_final_sha256": "trusted_verifiers.json",
}
_VERIFIER_RECORD_FIELDS = {
    "schema_version",
    "index",
    "name",
    "mode",
    "when",
    "phase",
    "command",
    "expected_exit_code",
    "exit_code",
    "status",
    "passed",
    "timed_out",
    "duration_seconds",
    "started_at",
    "finished_at",
    "stdout_path",
    "stderr_path",
    "stdout_bytes",
    "stderr_bytes",
    "stdout_sha256",
    "stderr_sha256",
    "errors",
}


def validate_fanout_manifest(manifest: dict[str, Any], *, task_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0":
        errors.append("unsupported fanout manifest schema version")
    if task_id is not None and manifest.get("task_id") != task_id:
        errors.append("fanout manifest task_id does not match the requested task")
    rollouts = manifest.get("rollouts")
    if not isinstance(rollouts, list) or len(rollouts) < 2:
        errors.append("fanout manifest requires at least two rollouts")
        return errors
    ids: list[str] = []
    workers: list[str] = []
    families: list[str] = []
    objectives: list[str] = []
    for index, rollout in enumerate(rollouts):
        prefix = f"rollouts[{index}]"
        if not isinstance(rollout, dict):
            errors.append(f"{prefix} must be an object")
            continue
        extra = sorted(set(rollout) - _ROLLOUT_FIELDS)
        if extra:
            errors.append(f"{prefix} has unsupported fields: {extra}")
        for field in (
            "rollout_id",
            "worker",
            "method_family",
            "context_mode",
            "objective",
        ):
            if not isinstance(rollout.get(field), str) or not rollout[field].strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        if rollout.get("context_mode") not in CONTEXT_MODES:
            errors.append(f"{prefix}.context_mode is invalid")
        ids.append(str(rollout.get("rollout_id", "")))
        workers.append(str(rollout.get("worker", "")))
        families.append(" ".join(str(rollout.get("method_family", "")).lower().split()))
        objectives.append(" ".join(str(rollout.get("objective", "")).lower().split()))
        for field in ("route_ids", "forbidden_methods", "required_controls"):
            values = rollout.get(field, [])
            if not isinstance(values, list) or not all(
                isinstance(value, str) and value.strip() for value in values
            ):
                errors.append(f"{prefix}.{field} must be an array of non-empty strings")
            elif len(values) != len(set(values)):
                errors.append(f"{prefix}.{field} must not contain duplicates")
        if not rollout.get("required_controls"):
            errors.append(f"{prefix}.required_controls must contain at least one falsifiable control")
    if len(ids) != len(set(ids)):
        errors.append("rollout_id values must be unique")
    if len(workers) != len(set(workers)):
        errors.append("worker labels must be unique within a breadth ensemble")
    if len(families) != len(set(families)):
        errors.append("sealed breadth rollouts must use distinct method_family values")
    if len(objectives) != len(set(objectives)):
        errors.append("sealed breadth rollouts must use distinct mathematical objectives")
    return errors


def load_fanout_manifest(path: Path, *, task_id: str | None = None) -> dict[str, Any]:
    manifest = read_json(path)
    errors = validate_fanout_manifest(manifest, task_id=task_id)
    if errors:
        raise ProtocolError("invalid fanout manifest: " + "; ".join(errors))
    return manifest


def _safe_relative_path(raw: Any) -> bool:
    if (
        not isinstance(raw, str)
        or not raw.strip()
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


def _resolve_from_root(root: Path, path: Path) -> Path:
    return (path if path.is_absolute() else root / path).resolve()


def _manifest_lineage(root: Path, manifest_path: Path) -> tuple[Path, str, str]:
    """Return a portable, repository-owned manifest identity."""

    root = root.resolve()
    resolved = _resolve_from_root(root, manifest_path)
    try:
        relative = resolved.relative_to(root)
    except ValueError as error:
        raise ProtocolError(
            "fanout manifest must be inside the repository so lineage remains portable"
        ) from error
    if not resolved.is_file():
        raise ProtocolError(f"fanout manifest does not exist: {relative.as_posix()}")
    return resolved, relative.as_posix(), sha256_file(resolved)


def _require_task_fanout_manifest(
    task: dict[str, Any], manifest_lineage: str
) -> None:
    """Enforce a task-declared official fanout manifest when one is present."""

    declared = task.get("fanout_manifest")
    if declared is None:
        return
    canonical = PurePosixPath(str(declared).replace("\\", "/")).as_posix()
    if declared != canonical or manifest_lineage != canonical:
        raise ProtocolError(
            "fanout manifest does not match the task-declared official manifest: "
            f"{canonical}"
        )


def _portable_run_dir(root: Path, task_id: str, run_dir: Path) -> tuple[Path, str]:
    """Validate and normalize one concrete task run directory."""

    root = root.resolve()
    task_runs = (root / "runs" / task_id).resolve()
    resolved = _resolve_from_root(root, run_dir)
    try:
        relative_task_run = resolved.relative_to(task_runs)
    except ValueError as error:
        raise ProtocolError("fanout runner returned a run outside its task directory") from error
    if len(relative_task_run.parts) != 1 or relative_task_run.name == "ensembles":
        raise ProtocolError("fanout runner must return one concrete task run directory")
    return resolved, resolved.relative_to(root).as_posix()


def _tree_sha256(files: dict[str, dict[str, Any]]) -> str:
    """Hash a canonical path/content/size tree for portable run evidence."""

    payload = json.dumps(
        files,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_tree_entry(path: Path) -> dict[str, Any]:
    return {"sha256": sha256_file(path), "bytes": path.stat().st_size}


def _validated_artifact_tree(
    root: Path,
    run_dir: Path,
    task_id: str,
    run_id: str,
    result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Recompute the exhaustive artifact tree and match its manifest/result."""

    artifact_dir = run_dir / "artifacts"
    manifest_path = run_dir / "artifact_manifest.json"
    if not artifact_dir.is_dir() or artifact_dir.is_symlink():
        raise ProtocolError("completed rollout is missing its artifacts directory")
    manifest = read_json(manifest_path)
    if set(manifest) != {"schema_version", "task_id", "run_id", "files"} or (
        manifest.get("schema_version") != "1.0"
        or manifest.get("task_id") != task_id
        or manifest.get("run_id") != run_id
    ):
        raise ProtocolError("completed rollout has an inconsistent artifact manifest")
    manifest_files = manifest.get("files")
    if not isinstance(manifest_files, list):
        raise ProtocolError("completed rollout artifact manifest files must be an array")

    actual: dict[str, dict[str, Any]] = {}
    for candidate in sorted(artifact_dir.rglob("*")):
        if candidate.is_symlink():
            raise ProtocolError("completed rollout artifacts cannot contain symbolic links")
        if not candidate.is_file():
            continue
        try:
            candidate.resolve().relative_to(artifact_dir.resolve())
            portable = candidate.resolve().relative_to(root).as_posix()
        except (OSError, ValueError) as error:
            raise ProtocolError("completed rollout artifact escapes its artifact directory") from error
        if portable in actual:
            raise ProtocolError("completed rollout artifact paths are not unique")
        actual[portable] = _file_tree_entry(candidate)

    recorded: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(manifest_files):
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256", "bytes"}:
            raise ProtocolError(f"artifact manifest files[{index}] is malformed")
        raw = entry.get("path")
        if not _safe_relative_path(raw):
            raise ProtocolError(f"artifact manifest files[{index}] has an unsafe path")
        path = (root / str(raw)).resolve()
        try:
            path.relative_to(artifact_dir.resolve())
            canonical = path.relative_to(root).as_posix()
        except (OSError, ValueError) as error:
            raise ProtocolError(
                f"artifact manifest files[{index}] is outside the run artifact directory"
            ) from error
        if raw != canonical or raw in recorded:
            raise ProtocolError(f"artifact manifest files[{index}] path is noncanonical or duplicate")
        if not path.is_file() or path.is_symlink():
            raise ProtocolError(f"artifact manifest file is missing or unsafe: {raw}")
        expected = _file_tree_entry(path)
        size = entry.get("bytes")
        if (
            not isinstance(entry.get("sha256"), str)
            or not isinstance(size, int)
            or isinstance(size, bool)
            or size < 0
            or entry.get("sha256") != expected["sha256"]
            or size != expected["bytes"]
        ):
            raise ProtocolError(f"artifact manifest content mismatch: {raw}")
        recorded[str(raw)] = expected
    if recorded != actual:
        missing = sorted(set(actual) - set(recorded))
        extra = sorted(set(recorded) - set(actual))
        raise ProtocolError(
            "artifact manifest is not exhaustive"
            f" (unrecorded={missing}, nonexistent={extra})"
        )

    result_artifacts = result.get("artifacts", [])
    if not isinstance(result_artifacts, list):
        raise ProtocolError("completed rollout result.artifacts must be an array")
    declared: set[str] = set()
    for index, artifact in enumerate(result_artifacts):
        if not isinstance(artifact, dict) or not _safe_relative_path(artifact.get("path")):
            raise ProtocolError(f"result.artifacts[{index}] has an unsafe or missing path")
        raw = artifact["path"]
        path = (root / raw).resolve()
        try:
            canonical = path.relative_to(root).as_posix()
            path.relative_to(artifact_dir.resolve())
        except (OSError, ValueError) as error:
            raise ProtocolError(f"result artifact is outside the run artifact directory: {raw}") from error
        if raw != canonical or raw in declared:
            raise ProtocolError(f"result artifact path is noncanonical or duplicate: {raw}")
        declared.add(raw)
    absent = sorted(declared - set(recorded))
    if absent:
        raise ProtocolError(f"result artifacts are absent from artifact_manifest.json: {absent}")
    return actual


def _dynamic_final_verifier_specs(task: dict[str, Any]) -> list[dict[str, Any]]:
    specs = [dict(spec) for spec in task.get("verifiers", [])]
    for index, raw in enumerate(task.get("dynamic_verifier_artifacts", []), start=1):
        specs.append(
            {
                "name": f"agent-produced exact control {index}: {raw}",
                "command": ["{python}", f"{{artifact_dir}}/{raw}"],
                "mode": "exact",
                "timeout_seconds": 600,
                "expected_exit_code": 0,
                "when": "final",
            }
        )
    return specs


def _portable_command_matches(
    expected: list[str],
    recorded: Any,
    *,
    source_root: str,
    artifact_relative: str,
) -> bool:
    """Match a verifier argv while tolerating transport to a different root."""

    if not isinstance(recorded, list) or len(recorded) != len(expected) or not source_root:
        return False
    normalized_root = source_root.replace("\\", "/")
    if len(normalized_root) > 1 and not (
        len(normalized_root) == 3 and normalized_root[1:] == ":/"
    ):
        normalized_root = normalized_root.rstrip("/")
    normalized_artifacts = f"{normalized_root.rstrip('/')}/{artifact_relative}"
    if normalized_root == "/":
        normalized_artifacts = f"/{artifact_relative}"
    python_source = len(expected) > 2 and expected[1] == "-c"
    for index, (template, value) in enumerate(zip(expected, recorded)):
        if not isinstance(value, str) or not value:
            return False
        if template == "{python}":
            if index != 0 or PurePosixPath(value.replace("\\", "/")).name.casefold() not in {
                "python",
                "python.exe",
                "python3",
                "python3.exe",
                "pypy",
                "pypy.exe",
                "pypy3",
                "pypy3.exe",
            }:
                return False
            continue
        if python_source and index == 2:
            portable_expected = template
        else:
            portable_expected = (
                template.replace("{root}", normalized_root)
                .replace("{artifact_dir}", normalized_artifacts)
            )
        if value.replace("\\", "/") != portable_expected.replace("\\", "/"):
            return False
    return True


def _validated_verifier_tree(
    root: Path,
    run_dir: Path,
    task: dict[str, Any],
    invocation: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Validate trusted reports and recompute every referenced verifier log."""

    task_id = task["task_id"]
    run_id = run_dir.name
    preflight_path = run_dir / "trusted_verifiers.preflight.json"
    final_path = run_dir / "trusted_verifiers.json"
    preflight = read_json(preflight_path)
    final = read_json(final_path)
    if set(preflight) != {
        "schema_version", "task_id", "run_id", "phase", "status", "records", "errors"
    } or (
        preflight.get("schema_version") != "1.0"
        or preflight.get("task_id") != task_id
        or preflight.get("run_id") != run_id
        or preflight.get("phase") != "preflight"
        or preflight.get("errors") != []
    ):
        raise ProtocolError("completed rollout has an inconsistent trusted preflight report")
    if set(final) != {"schema_version", "task_id", "run_id", "records", "errors"} or (
        final.get("schema_version") != "1.0"
        or final.get("task_id") != task_id
        or final.get("run_id") != run_id
        or final.get("errors") != []
    ):
        raise ProtocolError("completed rollout has an inconsistent trusted final report")

    base_specs = [dict(spec) for spec in task.get("verifiers", [])]
    expected_preflight = [
        (index, spec)
        for index, spec in enumerate(base_specs)
        if spec.get("when", "final") in {"preflight", "both"}
    ]
    all_final_specs = _dynamic_final_verifier_specs(task)
    expected_final = [
        (index, spec)
        for index, spec in enumerate(all_final_specs)
        if spec.get("when", "final") in {"final", "both"}
    ]
    preflight_status = "passed" if expected_preflight else "not_configured"
    if preflight.get("status") != preflight_status:
        raise ProtocolError("trusted preflight status does not match task verifier configuration")
    invocation_preflight = invocation.get("preflight_verifiers")
    expected_preflight_path = preflight_path.relative_to(root).as_posix()
    if invocation_preflight != {
        "path": expected_preflight_path,
        "status": preflight_status,
        "valid": True,
    }:
        raise ProtocolError("invocation preflight summary does not match its trusted report")

    source_root = invocation.get("cwd")
    if not isinstance(source_root, str) or not source_root.strip():
        raise ProtocolError("completed rollout invocation has no portable source cwd")
    artifact_relative = (run_dir / "artifacts").relative_to(root).as_posix()
    logs_dir = run_dir / "verifiers"
    log_tree: dict[str, dict[str, Any]] = {}

    def validate_records(
        raw_records: Any,
        expected: list[tuple[int, dict[str, Any]]],
        phase: str,
    ) -> None:
        if not isinstance(raw_records, list) or len(raw_records) != len(expected):
            raise ProtocolError(f"trusted {phase} verifier record set does not match the task")
        for position, (record, (index, spec)) in enumerate(zip(raw_records, expected)):
            if not isinstance(record, dict) or set(record) != _VERIFIER_RECORD_FIELDS:
                raise ProtocolError(f"trusted {phase} verifier record {position} is malformed")
            duration = record.get("duration_seconds")
            if (
                record.get("schema_version") != "1.0"
                or not isinstance(record.get("index"), int)
                or isinstance(record.get("index"), bool)
                or record.get("index") != index
                or record.get("name") != spec["name"]
                or record.get("mode") != spec["mode"]
                or record.get("when") != spec.get("when", "final")
                or record.get("phase") != phase
                or not isinstance(record.get("expected_exit_code"), int)
                or isinstance(record.get("expected_exit_code"), bool)
                or not isinstance(record.get("exit_code"), int)
                or isinstance(record.get("exit_code"), bool)
                or record.get("expected_exit_code") != spec["expected_exit_code"]
                or record.get("exit_code") != spec["expected_exit_code"]
                or record.get("status") != "passed"
                or record.get("passed") is not True
                or record.get("timed_out") is not False
                or record.get("errors") != []
                or not isinstance(duration, (int, float))
                or isinstance(duration, bool)
                or not math.isfinite(float(duration))
                or float(duration) < 0.0
                or not isinstance(record.get("started_at"), str)
                or not record.get("started_at")
                or not isinstance(record.get("finished_at"), str)
                or not record.get("finished_at")
                or not _portable_command_matches(
                    spec["command"],
                    record.get("command"),
                    source_root=source_root,
                    artifact_relative=artifact_relative,
                )
            ):
                raise ProtocolError(f"trusted {phase} verifier record {position} did not pass as declared")
            for stream in ("stdout", "stderr"):
                raw = record.get(f"{stream}_path")
                if not _safe_relative_path(raw):
                    raise ProtocolError(f"trusted verifier has unsafe {stream} path")
                path = (root / str(raw)).resolve()
                try:
                    path.relative_to(logs_dir.resolve())
                    canonical = path.relative_to(root).as_posix()
                except (OSError, ValueError) as error:
                    raise ProtocolError(f"trusted verifier {stream} path escapes run logs") from error
                if raw != canonical or raw in log_tree or not path.is_file() or path.is_symlink():
                    raise ProtocolError(f"trusted verifier {stream} path is missing or noncanonical")
                actual = _file_tree_entry(path)
                recorded_size = record.get(f"{stream}_bytes")
                if (
                    not isinstance(recorded_size, int)
                    or isinstance(recorded_size, bool)
                    or recorded_size < 0
                    or not isinstance(record.get(f"{stream}_sha256"), str)
                    or recorded_size != actual["bytes"]
                    or record.get(f"{stream}_sha256") != actual["sha256"]
                ):
                    raise ProtocolError(f"trusted verifier {stream} log content mismatch")
                log_tree[str(raw)] = actual

    validate_records(preflight.get("records"), expected_preflight, "preflight")
    validate_records(final.get("records"), expected_final, "final")
    actual_logs: dict[str, dict[str, Any]] = {}
    if logs_dir.exists():
        if not logs_dir.is_dir() or logs_dir.is_symlink():
            raise ProtocolError("completed rollout verifier log directory is unsafe")
        for candidate in sorted(logs_dir.rglob("*")):
            if candidate.is_symlink():
                raise ProtocolError("completed rollout verifier logs cannot contain symbolic links")
            if candidate.is_file():
                raw = candidate.resolve().relative_to(root).as_posix()
                actual_logs[raw] = _file_tree_entry(candidate)
    if actual_logs != log_tree:
        raise ProtocolError("trusted verifier reports do not exhaustively cover verifier logs")
    return log_tree


def _validated_run_attestation(
    root: Path,
    task_id: str,
    strategy: dict[str, Any] | None,
    run_dir: Path,
    *,
    recorded: Any = None,
) -> tuple[str, dict[str, str]]:
    """Authenticate a completed run and optionally match recorded file hashes."""

    root = root.resolve()
    resolved, relative = _portable_run_dir(root, task_id, run_dir)
    rollout_label = (
        str(strategy.get("rollout_id", resolved.name))
        if isinstance(strategy, dict)
        else resolved.name
    )
    paths = {
        label: resolved / filename for label, filename in _RUN_ATTESTATION_FILES.items()
    }
    missing = [
        path.name for path in paths.values() if not path.is_file() or path.is_symlink()
    ]
    if missing:
        raise ProtocolError(
            f"completed run {rollout_label} is missing run files: {sorted(missing)}"
        )

    invocation = read_json(paths["invocation_sha256"])
    task_snapshot = read_json(paths["task_sha256"])
    validation = read_json(paths["validation_sha256"])
    result = read_json(paths["result_sha256"])
    task = load_task(root, task_id)
    if invocation.get("repository_source_snapshot") != repository_source_snapshot(
        root, task
    ):
        raise ProtocolError(
            f"completed run {rollout_label} repository source snapshot mismatch"
        )
    expected_run_id = resolved.name
    invocation_worker = invocation.get("worker")
    expected_worker = strategy.get("worker") if isinstance(strategy, dict) else invocation_worker
    active_seconds = invocation.get("active_research_seconds")
    exit_code = invocation.get("exit_code")
    minimum_active_seconds = 60.0 * load_iteration_policy(root)[
        "minimum_active_minutes_per_worker"
    ]
    phases = invocation.get("phases")
    phase_seconds: list[float] = []
    phases_valid = isinstance(phases, list) and bool(phases)
    if phases_valid:
        for index, phase in enumerate(phases, start=1):
            seconds = phase.get("active_seconds") if isinstance(phase, dict) else None
            phase_exit = phase.get("exit_code") if isinstance(phase, dict) else None
            if (
                not isinstance(phase, dict)
                or phase.get("phase") != index
                or not isinstance(phase_exit, int)
                or isinstance(phase_exit, bool)
                or phase_exit != 0
                or not isinstance(seconds, (int, float))
                or isinstance(seconds, bool)
                or not math.isfinite(float(seconds))
                or float(seconds) < 0.0
            ):
                phases_valid = False
                break
            phase_seconds.append(float(seconds))
    phase_total = math.fsum(phase_seconds)
    if (
        invocation.get("schema_version") != "1.0"
        or invocation.get("task_id") != task_id
        or invocation.get("run_id") != expected_run_id
        or not isinstance(expected_worker, str)
        or not expected_worker.strip()
        or invocation_worker != expected_worker
        or invocation.get("dry_run") is not False
        or invocation.get("iteration_complete") is not True
        or not isinstance(exit_code, int)
        or isinstance(exit_code, bool)
        or exit_code != 0
        or invocation.get("rollout_strategy") != strategy
        or not isinstance(active_seconds, (int, float))
        or isinstance(active_seconds, bool)
        or not math.isfinite(float(active_seconds))
        or float(active_seconds) + 1e-6 < minimum_active_seconds
        or not phases_valid
        or not math.isclose(
            phase_total,
            float(active_seconds),
            rel_tol=1e-12,
            abs_tol=1e-6,
        )
    ):
        raise ProtocolError(
            f"completed run {rollout_label} has inconsistent invocation lineage"
        )
    if (
        set(validation) != {"valid", "errors"}
        or validation.get("valid") is not True
        or validation.get("errors") != []
    ):
        raise ProtocolError(f"completed run {rollout_label} has invalid validation")
    if task_snapshot != task:
        raise ProtocolError(
            f"completed run {rollout_label} task snapshot does not match the current task"
        )
    if (
        result.get("schema_version") != "1.0"
        or result.get("task_id") != task_id
        or result.get("run_id") != expected_run_id
        or result.get("worker") != expected_worker
    ):
        raise ProtocolError(f"completed run {rollout_label} has inconsistent result lineage")

    artifact_tree = _validated_artifact_tree(
        root, resolved, task_id, expected_run_id, result
    )
    verifier_tree = _validated_verifier_tree(root, resolved, task, invocation)
    attestation = {name: sha256_file(path) for name, path in paths.items()}
    attestation.update(
        {
            "artifact_tree_sha256": _tree_sha256(artifact_tree),
            "verifier_log_tree_sha256": _tree_sha256(verifier_tree),
        }
    )
    if recorded is not None:
        if not isinstance(recorded, dict) or set(recorded) != set(attestation):
            raise ProtocolError(
                f"completed run {rollout_label} has malformed run attestation"
            )
        mismatched = [name for name, digest in attestation.items() if recorded.get(name) != digest]
        if mismatched:
            raise ProtocolError(
                f"completed run {rollout_label} run attestation SHA-256 mismatch: "
                + ", ".join(sorted(mismatched))
            )
    return relative, attestation


def _ensemble_output_path(root: Path, task_id: str) -> tuple[str, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ensemble_id = f"ensemble-{stamp}-{uuid.uuid4().hex[:8]}"
    ensemble_dir = root / "runs" / task_id / "ensembles" / ensemble_id
    ensemble_dir.mkdir(parents=True, exist_ok=False)
    return ensemble_id, ensemble_dir / "ensemble.json"


def run_fanout(
    root: Path,
    task_id: str,
    manifest_path: Path,
    *,
    codex: str = "codex",
    model: str | None = None,
    max_parallel: int = 4,
    dry_run: bool = False,
    rollout_ids: list[str] | None = None,
    runner: Callable[..., Path] | None = None,
) -> Path:
    """Run independent RPCD rollouts and persist an ensemble lineage manifest.

    The default runner is imported lazily to avoid a module cycle and to make
    dry orchestration unit-testable without launching Codex.
    """

    root = root.resolve()
    task = load_task(root, task_id)
    resolved_manifest, manifest_lineage, manifest_hash = _manifest_lineage(
        root, manifest_path
    )
    _require_task_fanout_manifest(task, manifest_lineage)
    manifest = load_fanout_manifest(resolved_manifest, task_id=task_id)
    if task.get("research_mode") == "sealed_breadth":
        expected_context = task.get("context_policy", {}).get("mode", "statement_only")
        mismatched = [
            rollout["rollout_id"]
            for rollout in manifest["rollouts"]
            if rollout.get("context_mode") != expected_context
        ]
        if mismatched:
            raise ProtocolError(
                "sealed fanout context must match the task context policy; mismatched rollouts: "
                + ", ".join(mismatched)
            )
    if max_parallel < 1:
        raise ProtocolError("max_parallel must be positive")
    if runner is None:
        from .codex_adapter import run_codex_task

        runner = run_codex_task
    selected_mode = rollout_ids is not None
    if selected_mode:
        assert rollout_ids is not None
        if not rollout_ids:
            raise ProtocolError("at least one --rollout-id is required in shard mode")
        if not all(isinstance(rollout_id, str) and rollout_id.strip() for rollout_id in rollout_ids):
            raise ProtocolError("--rollout-id values must be non-empty strings")
        if len(rollout_ids) != len(set(rollout_ids)):
            raise ProtocolError("--rollout-id values must not contain duplicates")
        known_ids = {rollout["rollout_id"] for rollout in manifest["rollouts"]}
        unknown = sorted(set(rollout_ids) - known_ids)
        if unknown:
            raise ProtocolError(f"unknown rollout_id values: {unknown}")
        selected_ids = set(rollout_ids)
        strategies = [
            rollout for rollout in manifest["rollouts"] if rollout["rollout_id"] in selected_ids
        ]
    else:
        strategies = list(manifest["rollouts"])
    ensemble_id, output_path = _ensemble_output_path(root, task_id)

    def launch(strategy: dict[str, Any]) -> dict[str, Any]:
        try:
            run_dir = runner(
                root,
                task_id,
                worker=strategy["worker"],
                codex=codex,
                model=model,
                dry_run=dry_run,
                rollout_strategy=strategy,
            )
            resolved_run, relative_run = _portable_run_dir(root, task_id, run_dir)
            record = {
                "rollout_id": strategy["rollout_id"],
                "worker": strategy["worker"],
                "method_family": strategy["method_family"],
                "status": "prepared" if dry_run else "completed",
                "run_dir": relative_run,
            }
            if not dry_run:
                _, attestation = _validated_run_attestation(
                    root, task_id, strategy, resolved_run
                )
                record["run_attestation"] = attestation
            return record
        except Exception as error:  # preserve other independent rollouts
            portable_error = f"{type(error).__name__}: {error}"
            portable_error = portable_error.replace(str(root), ".")
            return {
                "rollout_id": strategy.get("rollout_id"),
                "worker": strategy.get("worker"),
                "method_family": strategy.get("method_family"),
                "status": "failed",
                "error": portable_error,
            }

    if dry_run or max_parallel == 1:
        records = [launch(strategy) for strategy in strategies]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
            records = list(executor.map(launch, strategies))
    output = {
        "schema_version": "1.0",
        "kind": "rpcd-independent-rollout-ensemble",
        "ensemble_id": ensemble_id,
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "dry_run": dry_run,
        "complete": not selected_mode,
        "source_manifest": manifest_lineage,
        "source_manifest_sha256": manifest_hash,
        "selected_rollout_ids": [strategy["rollout_id"] for strategy in strategies],
        "distinct_method_families": sorted({record["method_family"] for record in records}),
        "rollouts": records,
    }
    write_json(output_path, output)
    return output_path


def _load_shard(
    root: Path,
    task_id: str,
    shard_path: Path,
    *,
    manifest_lineage: str,
    manifest_hash: str,
) -> tuple[Path, str, dict[str, Any]]:
    """Load one repository-local, non-dry incomplete shard record."""

    root = root.resolve()
    resolved = _resolve_from_root(root, shard_path)
    ensemble_root = (root / "runs" / task_id / "ensembles").resolve()
    try:
        relative = resolved.relative_to(ensemble_root)
    except ValueError as error:
        raise ProtocolError("fanout shard must be inside this task's ensembles directory") from error
    if len(relative.parts) != 2 or relative.name != "ensemble.json":
        raise ProtocolError("fanout shard must be runs/<task>/ensembles/<id>/ensemble.json")
    shard = read_json(resolved)
    expected_id = relative.parts[0]
    if (
        shard.get("schema_version") != "1.0"
        or shard.get("kind") != "rpcd-independent-rollout-ensemble"
        or shard.get("ensemble_id") != expected_id
        or shard.get("task_id") != task_id
    ):
        raise ProtocolError(f"fanout shard has inconsistent task or ensemble identity: {relative}")
    if shard.get("dry_run") is not False:
        raise ProtocolError(f"fanout shard must be non-dry: {relative}")
    if shard.get("complete") is not False:
        raise ProtocolError(f"fanout shard must have complete=false: {relative}")
    if (
        shard.get("source_manifest") != manifest_lineage
        or shard.get("source_manifest_sha256") != manifest_hash
    ):
        raise ProtocolError(f"fanout shard source manifest lineage mismatch: {relative}")
    rollouts = shard.get("rollouts")
    if not isinstance(rollouts, list) or not rollouts:
        raise ProtocolError(f"fanout shard has no rollout records: {relative}")
    selected = shard.get("selected_rollout_ids")
    record_ids = [
        record.get("rollout_id") for record in rollouts if isinstance(record, dict)
    ]
    if (
        not isinstance(selected, list)
        or len(record_ids) != len(rollouts)
        or selected != record_ids
        or len(record_ids) != len(set(record_ids))
    ):
        raise ProtocolError(f"fanout shard selection does not match its rollout records: {relative}")
    return resolved, resolved.relative_to(root).as_posix(), shard


def merge_fanout_shards(
    root: Path,
    task_id: str,
    manifest_path: Path,
    shard_paths: list[Path],
) -> Path:
    """Merge transported shard ensembles into one fully validated ensemble."""

    root = root.resolve()
    task = load_task(root, task_id)
    resolved_manifest, manifest_lineage, manifest_hash = _manifest_lineage(
        root, manifest_path
    )
    _require_task_fanout_manifest(task, manifest_lineage)
    manifest = load_fanout_manifest(resolved_manifest, task_id=task_id)
    if not shard_paths:
        raise ProtocolError("fanout-merge requires at least one --shard")

    resolved_shards = [_resolve_from_root(root, path) for path in shard_paths]
    if len(resolved_shards) != len(set(resolved_shards)):
        raise ProtocolError("fanout-merge shard paths must not contain duplicates")
    expected = {rollout["rollout_id"]: rollout for rollout in manifest["rollouts"]}
    records_by_id: dict[str, dict[str, Any]] = {}
    seen_run_dirs: set[str] = set()
    source_shards: list[dict[str, str]] = []

    for shard_path in shard_paths:
        resolved_shard, shard_relative, shard = _load_shard(
            root,
            task_id,
            shard_path,
            manifest_lineage=manifest_lineage,
            manifest_hash=manifest_hash,
        )
        shard_hash = sha256_file(resolved_shard)
        source_shards.append({"path": shard_relative, "sha256": shard_hash})
        for record in shard["rollouts"]:
            rollout_id = record["rollout_id"]
            if rollout_id in records_by_id:
                raise ProtocolError(f"duplicate rollout_id across fanout shards: {rollout_id}")
            strategy = expected.get(rollout_id)
            if strategy is None:
                raise ProtocolError(f"fanout shard contains unknown rollout_id: {rollout_id}")
            if record.get("status") != "completed":
                raise ProtocolError(f"fanout shard rollout is not completed: {rollout_id}")
            if any(
                record.get(field) != strategy[field]
                for field in ("worker", "method_family")
            ):
                raise ProtocolError(f"fanout shard rollout metadata mismatch: {rollout_id}")
            raw_run_dir = record.get("run_dir")
            if not _safe_relative_path(raw_run_dir):
                raise ProtocolError(f"fanout shard has unsafe run_dir: {rollout_id}")
            run_dir = (root / str(raw_run_dir)).resolve()
            relative_run, attestation = _validated_run_attestation(
                root,
                task_id,
                strategy,
                run_dir,
                recorded=record.get("run_attestation"),
            )
            if relative_run != raw_run_dir:
                raise ProtocolError(f"fanout shard run_dir is not canonical: {rollout_id}")
            if relative_run in seen_run_dirs:
                raise ProtocolError(f"duplicate run_dir across fanout shards: {relative_run}")
            seen_run_dirs.add(relative_run)
            merged_record = dict(record)
            merged_record["run_attestation"] = attestation
            merged_record["source_shard"] = shard_relative
            merged_record["source_shard_sha256"] = shard_hash
            records_by_id[rollout_id] = merged_record

    missing = [rollout_id for rollout_id in expected if rollout_id not in records_by_id]
    if missing:
        raise ProtocolError(f"fanout shards do not cover manifest rollout_ids: {missing}")

    records = [records_by_id[rollout["rollout_id"]] for rollout in manifest["rollouts"]]
    ensemble_id, output_path = _ensemble_output_path(root, task_id)
    output = {
        "schema_version": "1.0",
        "kind": "rpcd-independent-rollout-ensemble",
        "ensemble_id": ensemble_id,
        "task_id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "dry_run": False,
        "complete": True,
        "source_manifest": manifest_lineage,
        "source_manifest_sha256": manifest_hash,
        "selected_rollout_ids": [rollout["rollout_id"] for rollout in manifest["rollouts"]],
        "distinct_method_families": sorted(
            {rollout["method_family"] for rollout in manifest["rollouts"]}
        ),
        "source_shards": source_shards,
        "rollouts": records,
    }
    write_json(output_path, output)
    return output_path
