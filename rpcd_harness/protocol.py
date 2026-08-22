"""Task, result, claim-ledger, and checkpoint validation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


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
    path = PurePosixPath(raw.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts and raw.strip() != ""


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
    if root is not None:
        for raw in task["inputs"]:
            if not _safe_relative_path(raw):
                raise ProtocolError(f"unsafe task input path: {raw}")
            if not (root / raw).exists():
                raise ProtocolError(f"task input does not exist: {raw}")


def validate_result(
    result: dict[str, Any],
    task: dict[str, Any] | None = None,
    *,
    iteration_policy: dict[str, Any] | None = None,
    active_seconds: float | None = None,
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

    for index, artifact in enumerate(result.get("artifacts", [])):
        raw = artifact.get("path", "") if isinstance(artifact, dict) else ""
        if not _safe_relative_path(raw):
            errors.append(f"artifacts[{index}]: unsafe relative path {raw!r}")

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
        elif len(avenues) < policy["minimum_distinct_avenues"]:
            errors.append(
                "iteration has too few distinct avenues: "
                f"{len(avenues)} < {policy['minimum_distinct_avenues']}"
            )
        if not isinstance(checkpoints, list):
            errors.append("iteration.checkpoints must be an array")
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
    resolved_run = run_dir.resolve()
    try:
        relative_run = resolved_run.relative_to(root.resolve())
    except ValueError as error:
        raise ProtocolError("run directory must be inside the repository") from error
    if not resolved_run.is_dir():
        raise ProtocolError(f"run directory does not exist: {run_dir}")
    entries = []
    for path in sorted(resolved_run.rglob("*")):
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
        "files": entries,
    }
    output = root / "research" / "checkpoints" / f"{task_id}--{run_id}.json"
    write_json(output, checkpoint)
    return output


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
        if status == "theorem_candidate":
            required_gates = ["proof_draft", "hostile_audit", "independent_reconstruction", "priority_audit"]
            missing = [gate for gate in required_gates if not gates.get(gate)]
            if EVIDENCE_RANK[level] < 5:
                errors.append(f"{label}: theorem_candidate must be at least E5")
            if missing:
                errors.append(f"{label}: theorem_candidate missing gates {missing}")
        if status == "external_theorem" and claim.get("origin", {}).get("kind") != "external_theorem":
            errors.append(f"{label}: external theorem lacks an external_theorem origin")
    return errors
