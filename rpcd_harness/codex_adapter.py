"""Run self-contained research tasks through the local Codex CLI."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .protocol import (
    ProtocolError,
    load_iteration_policy,
    load_task,
    read_json,
    sha256_file,
    validate_result,
    write_json,
)


def new_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def render_prompt(
    root: Path,
    task: dict[str, Any],
    run_id: str,
    worker: str,
    output_dir: Path,
    iteration_policy: dict[str, Any],
    *,
    phase: int = 1,
    accumulated_active_seconds: float = 0.0,
    previous_result: Path | None = None,
) -> str:
    common = (root / "prompts" / "common.md").read_text(encoding="utf-8")
    role = (root / "prompts" / f"{task['role']}.md").read_text(encoding="utf-8")
    task_json = json.dumps(task, ensure_ascii=False, indent=2)
    policy_json = json.dumps(iteration_policy, ensure_ascii=False, indent=2)
    relative_output = output_dir.relative_to(root).as_posix()
    continuation = ""
    if previous_result is not None:
        relative_previous = previous_result.relative_to(root).as_posix()
        continuation = f"""

# Continuation pass

This is research pass {phase}. Earlier passes accumulated
`{accumulated_active_seconds / 60.0:.2f}` active minutes. Continuation is mandatory until both the
active-time floor and the structured-result validation contract are satisfied. Read
`{relative_previous}`, its sibling phase validation report, and every artifact it references.
Continue cumulatively: preserve valid earlier claims/checkpoints/failures, but attack a genuinely
new proof route or a deeper unresolved objection. The result of this pass must summarize the whole
iteration, not only this pass.
"""
    return f"""{common}\n\n{role}\n\n# Assigned task\n\n```json\n{task_json}\n```\n\n# Iteration policy\n\n```json\n{policy_json}\n```\n\nRun metadata:\n- run_id: `{run_id}`\n- worker: `{worker}`\n- research pass: `{phase}`\n- repository root: current working directory\n- durable output directory: `{relative_output}`\n{continuation}\n\nRead the task inputs now. Work autonomously within this task's scope. Run the required checks.\nDo not idle merely to consume the time floor; spend it deriving, falsifying, checking edge cases, and\nwriting portable artifacts. Add a substantive checkpoint about every\n`{iteration_policy['checkpoint_interval_minutes']}` active minutes.\nYour final JSON must use the exact task_id, run_id, and worker above. Artifact paths must be\nrelative to the repository root and must point inside `{relative_output}`.\n"""


def run_codex_task(
    root: Path,
    task_id: str,
    worker: str,
    codex: str = "codex",
    model: str | None = None,
    dry_run: bool = False,
) -> Path:
    task = load_task(root, task_id)
    iteration_policy = load_iteration_policy(root)
    run_id = new_run_id()
    run_dir = root / "runs" / task_id / run_id
    output_dir = run_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=False)
    prompt = render_prompt(root, task, run_id, worker, output_dir, iteration_policy)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    write_json(run_dir / "task.json", task)

    result_path = run_dir / "result.json"
    command_prefix = [
        codex,
        "exec",
        "--json",
        "--output-schema",
        str((root / "schemas" / "result.schema.json").resolve()),
    ]
    if model:
        command_prefix.extend(["--model", model])
    invocation = {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": run_id,
        "worker": worker,
        "cwd": str(root),
        "command_template": [*command_prefix, "-o", "<phase-result.json>", "-"],
        "dry_run": dry_run,
        "minimum_active_minutes_per_worker": iteration_policy[
            "minimum_active_minutes_per_worker"
        ],
        "credential_policy": "Uses local Codex authentication; no credential files are read or copied by the harness.",
    }
    write_json(run_dir / "invocation.json", invocation)
    if dry_run:
        return run_dir

    minimum_active_seconds = 60.0 * iteration_policy["minimum_active_minutes_per_worker"]
    accumulated_active_seconds = 0.0
    phases: list[dict[str, Any]] = []
    previous_result: Path | None = None
    phase = 0
    events_dir = run_dir / "events"
    events_dir.mkdir()
    while True:
        phase += 1
        phase_result = run_dir / f"phase-{phase:03d}-result.json"
        phase_prompt = render_prompt(
            root,
            task,
            run_id,
            worker,
            output_dir,
            iteration_policy,
            phase=phase,
            accumulated_active_seconds=accumulated_active_seconds,
            previous_result=previous_result,
        )
        prompt_path = run_dir / f"phase-{phase:03d}-prompt.md"
        prompt_path.write_text(phase_prompt, encoding="utf-8")
        events_path = events_dir / f"phase-{phase:03d}.jsonl"
        stderr_path = events_dir / f"phase-{phase:03d}.stderr.log"
        command = [*command_prefix, "-o", str(phase_result.resolve()), "-"]
        phase_started_at = datetime.now(timezone.utc)
        monotonic_start = time.monotonic()
        try:
            with events_path.open("w", encoding="utf-8") as events, stderr_path.open(
                "w", encoding="utf-8"
            ) as errors:
                completed = subprocess.run(
                    command,
                    input=phase_prompt,
                    text=True,
                    cwd=root,
                    stdout=events,
                    stderr=errors,
                    check=False,
                )
        except OSError as error:
            write_json(
                run_dir / "launcher_error.json",
                {
                    "error": type(error).__name__,
                    "message": str(error),
                    "active_seconds_before_failure": accumulated_active_seconds,
                    "hint": "Install/enable the Codex CLI or pass --codex with an executable path.",
                },
            )
            raise ProtocolError(f"could not launch Codex: {error}") from error

        phase_seconds = time.monotonic() - monotonic_start
        accumulated_active_seconds += phase_seconds
        phase_record = {
            "phase": phase,
            "started_at": phase_started_at.isoformat().replace("+00:00", "Z"),
            "ended_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "active_seconds": phase_seconds,
            "cumulative_active_seconds": accumulated_active_seconds,
            "exit_code": completed.returncode,
            "prompt": prompt_path.relative_to(root).as_posix(),
            "result": phase_result.relative_to(root).as_posix(),
            "events": events_path.relative_to(root).as_posix(),
            "stderr": stderr_path.relative_to(root).as_posix(),
        }
        phases.append(phase_record)
        invocation["phases"] = phases
        invocation["active_research_seconds"] = accumulated_active_seconds
        invocation["iteration_complete"] = False
        write_json(run_dir / "invocation.json", invocation)

        if completed.returncode != 0:
            write_json(
                run_dir / "incomplete_iteration.json",
                {
                    "reason": "codex_phase_failed",
                    "required_active_seconds": minimum_active_seconds,
                    "completed_active_seconds": accumulated_active_seconds,
                    "last_phase": phase_record,
                    "portable_checkpoint": True,
                },
            )
            raise ProtocolError(
                f"Codex phase {phase} exited with code {completed.returncode}; see {stderr_path}"
            )
        if not phase_result.is_file():
            raise ProtocolError(f"Codex phase {phase} completed without producing a result")
        # A continuation pass receives the previous structured result and all common artifacts.
        # The final pass is required to report the iteration cumulatively.
        previous_result = phase_result

        phase_result_value = read_json(phase_result)
        phase_errors = validate_result(
            phase_result_value,
            task=task,
            iteration_policy=iteration_policy,
            active_seconds=(
                accumulated_active_seconds
                if accumulated_active_seconds + 1e-6 >= minimum_active_seconds
                else None
            ),
        )
        resolved_output = output_dir.resolve()
        for artifact in phase_result_value.get("artifacts", []):
            artifact_path = (root / artifact["path"]).resolve()
            try:
                artifact_path.relative_to(resolved_output)
            except ValueError:
                phase_errors.append(
                    f"artifact is outside the assigned output directory: {artifact['path']}"
                )
                continue
            if not artifact_path.exists():
                phase_errors.append(f"declared artifact does not exist: {artifact['path']}")
        write_json(
            run_dir / f"phase-{phase:03d}-validation.json",
            {
                "valid": not phase_errors,
                "minimum_active_time_reached": (
                    accumulated_active_seconds + 1e-6 >= minimum_active_seconds
                ),
                "errors": phase_errors,
            },
        )
        if (
            accumulated_active_seconds + 1e-6 >= minimum_active_seconds
            and not phase_errors
        ):
            break

    if previous_result is None:  # defensive; the positive policy floor makes this unreachable
        raise ProtocolError("iteration produced no research pass")
    shutil.copyfile(previous_result, result_path)
    invocation["exit_code"] = 0
    invocation["iteration_complete"] = True
    invocation["active_research_seconds"] = accumulated_active_seconds
    write_json(run_dir / "invocation.json", invocation)

    result = read_json(result_path)
    errors = validate_result(
        result,
        task=task,
        iteration_policy=iteration_policy,
        active_seconds=accumulated_active_seconds,
    )
    resolved_output = output_dir.resolve()
    for artifact in result.get("artifacts", []):
        artifact_path = (root / artifact["path"]).resolve()
        try:
            artifact_path.relative_to(resolved_output)
        except ValueError:
            errors.append(f"artifact is outside the assigned output directory: {artifact['path']}")
            continue
        if not artifact_path.exists():
            errors.append(f"declared artifact does not exist: {artifact['path']}")
    write_json(run_dir / "validation.json", {"valid": not errors, "errors": errors})
    if errors:
        raise ProtocolError("result failed protocol validation: " + "; ".join(errors))
    manifest_entries = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file():
            manifest_entries.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                }
            )
    write_json(
        run_dir / "artifact_manifest.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "files": manifest_entries,
        },
    )
    return run_dir
