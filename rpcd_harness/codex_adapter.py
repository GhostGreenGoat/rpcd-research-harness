"""Run self-contained research tasks through the local Codex CLI."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .protocol import (
    ProtocolError,
    dependency_result_paths,
    load_iteration_policy,
    load_resume_checkpoint,
    load_task,
    read_json,
    repository_source_snapshot,
    sha256_file,
    unmet_task_dependencies,
    validate_route_card,
    validate_result,
    write_json,
)
from .verifiers import run_verifiers


ROLLOUT_STRATEGY_FIELDS = {
    "rollout_id",
    "worker",
    "method_family",
    "context_mode",
    "route_ids",
    "objective",
    "forbidden_methods",
    "required_controls",
}


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
    rollout_strategy: dict[str, Any] | None = None,
    route_card_only: bool = False,
    route_card_sha256: str | None = None,
    preflight_report: Path | None = None,
    resume_context: dict[str, Any] | None = None,
) -> str:
    common = (root / "prompts" / "common.md").read_text(encoding="utf-8")
    role = (root / "prompts" / f"{task['role']}.md").read_text(encoding="utf-8")
    visible_task = deepcopy(task)
    strategy = {
        key: value
        for key, value in (rollout_strategy or {}).items()
        if key in ROLLOUT_STRATEGY_FIELDS
    }
    if strategy.get("objective"):
        visible_task["objective"] = strategy["objective"]
    if strategy.get("route_ids"):
        visible_task["route_ids"] = strategy["route_ids"]
    if strategy.get("method_family"):
        constraints = dict(visible_task.get("method_constraints", {}))
        base_family = constraints.get("method_family")
        constraints["method_family"] = strategy["method_family"]
        if base_family and strategy["method_family"] != base_family:
            # A breadth rollout must not inherit a representation-specific
            # requirement from the coordinator's default family.
            constraints.pop("required_differences", None)
        constraints["forbidden_methods"] = strategy.get(
            "forbidden_methods", constraints.get("forbidden_methods", [])
        )
        constraints["required_controls"] = strategy.get(
            "required_controls", constraints.get("required_controls", [])
        )
        visible_task["method_constraints"] = constraints
    if strategy.get("context_mode"):
        context = dict(visible_task.get("context_policy", {}))
        context["mode"] = strategy["context_mode"]
        visible_task["context_policy"] = context
    if route_card_only:
        context = visible_task.get("context_policy", {})
        visible_task["inputs"] = context.get("allowlist") or visible_task.get("inputs", [])[:1]
        visible_task["context_policy"] = {
            "mode": context.get("mode", "statement_only"),
            "allowlist": visible_task["inputs"],
            "reveal_after_route_card": True,
        }
        visible_task["acceptance_checks"] = [
            "Submit one immutable, falsifiable route card before inherited RPCD history is revealed."
        ]
        visible_task["required_artifacts"] = ["route_card.json"]
        assigned_family = strategy.get("method_family") or visible_task.get(
            "method_constraints", {}
        ).get("method_family", "self-chosen-new-family")
        visible_task["objective"] = (
            "From the minimal RPCD statement, commit to one falsifiable route in the assigned "
            "method family before any inherited derivation or failure map is revealed."
        )
        visible_task["method_constraints"] = {
            "method_family": assigned_family,
            "required_differences": [
                "Choose the representation, retained state, and first bridge lemma independently."
            ],
            "required_controls": [
                "Name an analytic falsifier for the first claimed implication edge."
            ],
        }
        # Trusted checks often encode names of prior constructions or barrier
        # scripts. They belong to the post-card pruning phase, not sealed idea
        # generation.
        visible_task["verifiers"] = []
    task_json = json.dumps(visible_task, ensure_ascii=False, indent=2)
    policy_json = json.dumps(iteration_policy, ensure_ascii=False, indent=2)
    relative_output = output_dir.relative_to(root).as_posix()
    continuation = ""
    if previous_result is not None:
        relative_previous = previous_result.relative_to(root).as_posix()
        if resume_context is not None:
            continuation = f"""

# Checkpoint continuation (not independent breadth)

This new run is a continuation-depth handoff from checkpoint
`{resume_context['checkpoint']}` and source run `{resume_context['source_run']}`. Its inherited
source phase result is `{resume_context['source_result']}`. For this pass, read
`{relative_previous}`, its sibling phase validation report, and the inherited artifact copies now
inside `{relative_output}`. The source run recorded
`{resume_context['source_active_minutes']:.2f}` active minutes, but those minutes are provenance only:
this run starts at `0.00` credited active minutes and must independently satisfy the full
`{iteration_policy['minimum_active_minutes_per_worker']}`-minute floor.

`independence=false`: deepen, repair, stress-test, or refute the already selected route. Do not
describe this handoff as a fresh statement-only discovery, an independent rollout, or additional
search width. Summarize inherited claims and failures cumulatively, and make every artifact claimed
by the new result point to its copy inside `{relative_output}`.
"""
        else:
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
    strategy_text = ""
    if strategy:
        visible_strategy = strategy
        if route_card_only:
            visible_strategy = {
                key: strategy[key]
                for key in (
                    "rollout_id",
                    "worker",
                    "method_family",
                    "context_mode",
                    "route_ids",
                )
                if key in strategy
            }
        strategy_heading = (
            "Inherited locked route strategy (independence=false)"
            if resume_context is not None
            else "Independent rollout strategy"
        )
        strategy_text = f"\n# {strategy_heading}\n\n```json\n" + json.dumps(
            visible_strategy, ensure_ascii=False, indent=2
        ) + "\n```\n"
    route_card_contract = ""
    if route_card_only:
        route_card_minutes = task.get("rollout_strategy", {}).get("route_card_minutes", 20)
        expected_rollout = strategy.get("rollout_id", task["task_id"])
        expected_family = strategy.get("method_family") or task.get("method_constraints", {}).get(
            "method_family", "self-chosen-new-family"
        )
        expected_context = strategy.get("context_mode") or task.get("context_policy", {}).get(
            "mode", "statement_only"
        )
        expected_parents = strategy.get("route_ids") or task.get("route_ids", [])
        route_card_contract = f"""

# Sealed route-card phase

This phase measures search breadth, not proof depth. Work only from the declared files staged in
the current directory. Do not search for or read inherited RPCD proofs, iteration reports, failure
maps, claims, route files, or external literature. Literature and novelty search begin only after
the mathematical card is locked. Within about {route_card_minutes} minutes, write `route_card.json` in
the current directory with exactly these fields:

`schema_version`, `route_card_id`, `task_id`, `rollout_id`, `method_family`, `representation`,
`state_or_invariant`,
`core_candidate_lemma`, `predicted_failure`, `falsifier`, `target_implication`,
`information_retained`, `information_discarded`, `context_mode`, `parent_route_ids`.

Use `task_id={task['task_id']}`, `rollout_id={expected_rollout}`,
`method_family={expected_family}`, and `context_mode={expected_context}` exactly.
Use `parent_route_ids={json.dumps(expected_parents, ensure_ascii=False)}` exactly so the route
cannot be retroactively attached to a more successful branch.

The route must make a mathematical prediction that a later exact, numerical, or formal verifier can
falsify. Do not perform an inherited-history proof attempt yet. The harness will hash this card;
later phases may test or refute it but may not edit it.
"""
    elif route_card_sha256:
        route_card_contract = f"""

# Locked route card

The statement-first card at `{relative_output}/route_card.json` has SHA-256
`{route_card_sha256}` and is immutable. You may now read the declared inherited inputs, test the
route against the failure map, and deepen it, branch at its first bad edge, or refute it. Do not
rewrite the card to imitate an inherited route.
"""
    route_result_contract = ""
    research_mode = task.get("research_mode")
    if not route_card_only and resume_context is not None:
        route_result_contract = """

# Resumed depth-route contract

Work only on the already locked mathematical route and its first unresolved implication edge.
This is continuation depth, even when the source task originally used sealed breadth to choose the
route. Preserve the immutable route card. A repaired lemma, a hostile falsifier, or an honest
refutation is useful; relabeling the route as a new independent avenue is forbidden.
"""
    elif not route_card_only and research_mode == "continuation_depth":
        route_result_contract = """

# Depth-route result contract

This task deepens an existing mathematical route. One substantive avenue is enough while its next
implication edge is genuinely advancing; do not invent cosmetic alternatives. If that edge is
blocked, refuted, suspended, or explicitly branched, report two mathematically distinct children:
one `branch_kind=repair` that restores the lost information and one `branch_kind=attack` that tries
to refute the same edge. In each reported avenue include `route_id`, `parent_route_ids`,
`source_layer`, `next_layer`, `branch_kind`, `first_bad_edge`, `core_candidate_lemma`,
`predicted_failure`, `falsifier`, and `decision`. The child layer must be immediately below the
source layer and at least one parent must be an assigned frontier route. Record the first failed
implication edge, not merely the final failure.
"""
    elif not route_card_only and research_mode == "critic_validation":
        route_result_contract = """

# Independent-critic result contract

Report at least two genuinely different attacks. Each avenue must include `representation`,
`first_bad_edge`, `predicted_failure`, `falsifier`, and `decision`; copying the candidate's own
checker is not an independent attack.
"""
    dependency_context = ""
    completed_dependencies = dependency_result_paths(root, task)
    if completed_dependencies and not route_card_only:
        dependency_context = (
            "\n# Completed dependency result packages\n\n"
            + "\n".join(f"- `{path}`" for path in completed_dependencies)
            + "\n\nRead each result and every artifact it declares before auditing or extending it.\n"
        )
    preflight_context = ""
    if preflight_report is not None and not route_card_only:
        relative_preflight = preflight_report.relative_to(root).as_posix()
        preflight_context = f"""

# Trusted preflight

The repository-owned cheap baseline checks passed before this research phase. Their structured
records and hashed logs are at `{relative_preflight}`. Treat this only as validation of inherited
identities and known barriers: it does not verify a new lemma or promote its evidence level.
"""
    execution_mode = "checkpoint_continuation" if resume_context is not None else "fresh_run"
    return f"""{common}\n\n{role}\n\n# Assigned task\n\n```json\n{task_json}\n```\n\n# Iteration policy\n\n```json\n{policy_json}\n```\n\nRun metadata:\n- run_id: `{run_id}`\n- worker: `{worker}`\n- execution mode: `{execution_mode}`\n- research pass: `{phase}`\n- repository root: current working directory\n- durable output directory: `{relative_output}`\n{continuation}{strategy_text}{route_card_contract}{route_result_contract}{dependency_context}{preflight_context}\n\nRead the task inputs now. Work autonomously within this task's scope. Run the required checks.\nDo not idle merely to consume the time floor; spend it deriving, falsifying, checking edge cases, and\nwriting portable artifacts. Add a substantive checkpoint about every\n`{iteration_policy['checkpoint_interval_minutes']}` active minutes.\nYour final JSON must use the exact task_id, run_id, and worker above. Artifact paths must be\nrelative to the repository root and must point inside `{relative_output}`.\n"""


def run_codex_task(
    root: Path,
    task_id: str,
    worker: str,
    codex: str = "codex",
    model: str | None = None,
    dry_run: bool = False,
    rollout_strategy: dict[str, Any] | None = None,
    allow_unmet_dependencies: bool = False,
    resume_from_checkpoint: Path | None = None,
) -> Path:
    root = root.resolve()
    if resume_from_checkpoint is not None and rollout_strategy is not None:
        raise ProtocolError(
            "checkpoint continuation cannot be launched as a new independent rollout"
        )
    unknown_strategy_fields = sorted(set(rollout_strategy or {}) - ROLLOUT_STRATEGY_FIELDS)
    if unknown_strategy_fields:
        raise ProtocolError(
            "rollout strategy has unsupported fields: " + ", ".join(unknown_strategy_fields)
        )
    task = load_task(root, task_id)
    resume_state = (
        load_resume_checkpoint(root, task_id, resume_from_checkpoint)
        if resume_from_checkpoint is not None
        else None
    )
    validation_rollout_strategy = (
        resume_state["validation_rollout_strategy"]
        if resume_state is not None
        else rollout_strategy
    )
    unmet = unmet_task_dependencies(root, task)
    independence_required = (
        task.get("research_mode") == "critic_validation"
        or task.get("require_distinct_dependency_workers", False)
    )
    if allow_unmet_dependencies and independence_required:
        raise ProtocolError(
            "the dependency override is not admissible for an independent audit/reconstruction task"
        )
    if unmet and not allow_unmet_dependencies:
        raise ProtocolError(
            "task has unmet dependencies: " + ", ".join(unmet) +
            "; use an explicit override only for recovery/audit work"
        )
    dependency_results = dependency_result_paths(root, task)
    if independence_required:
        dependency_worker_list: list[str] = []
        for raw in dependency_results:
            result_path = (root / raw).resolve()
            invocation_path = result_path.parent / "invocation.json"
            if not invocation_path.is_file():
                raise ProtocolError(
                    f"independence dependency lacks its harness invocation: {raw}"
                )
            dependency_invocation = read_json(invocation_path)
            dependency_worker = dependency_invocation.get("worker")
            if not isinstance(dependency_worker, str) or not dependency_worker.strip():
                raise ProtocolError(
                    f"independence dependency has no authenticated worker: {raw}"
                )
            dependency_worker_list.append(dependency_worker)
        dependency_workers = set(dependency_worker_list)
        if task.get("require_distinct_dependency_workers", False) and len(
            dependency_worker_list
        ) != len(dependency_workers):
            raise ProtocolError(
                "authenticated dependency workers must be mutually distinct"
            )
        if worker in dependency_workers:
            raise ProtocolError(
                "task worker must differ from every authenticated dependency worker"
            )
    iteration_policy = load_iteration_policy(root)
    if resume_state is not None:
        for inherited in resume_state["inherited_artifacts"]:
            parts = [part.lower() for part in inherited["relative_path"].split("/")]
            filename = parts[-1]
            if (
                ".codex" in parts
                or filename == "auth.json"
                or filename == ".env"
                or filename.startswith(".env.")
            ):
                raise ProtocolError(
                    "resume checkpoint artifact set contains a forbidden credential path: "
                    + inherited["source_path"]
                )
    run_id = new_run_id()
    run_dir = root / "runs" / task_id / run_id
    output_dir = run_dir / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=False)
    sealed_breadth = task.get("research_mode") == "sealed_breadth"
    previous_result: Path | None = None
    route_card_sha256: str | None = None
    resume_context: dict[str, Any] | None = None
    inherited_records: list[dict[str, Any]] = []
    if resume_state is not None:
        for inherited in resume_state["inherited_artifacts"]:
            source = root / inherited["source_path"]
            destination = output_dir.joinpath(*inherited["relative_path"].split("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            if sha256_file(destination) != inherited["sha256"]:
                raise ProtocolError(
                    "resume source artifact changed while it was being copied: "
                    + inherited["source_path"]
                )
            inherited_records.append(
                {
                    "source_path": inherited["source_path"],
                    "destination_path": destination.relative_to(root).as_posix(),
                    "sha256": inherited["sha256"],
                    "bytes": inherited["bytes"],
                }
            )
        inherited_state_dir = run_dir / "inherited"
        inherited_state_dir.mkdir()
        inherited_result = inherited_state_dir / resume_state["previous_result"].name
        inherited_validation = (
            inherited_state_dir / resume_state["previous_validation"].name
        )
        shutil.copy2(resume_state["previous_result"], inherited_result)
        shutil.copy2(resume_state["previous_validation"], inherited_validation)
        if sha256_file(inherited_result) != resume_state["previous_result_sha256"]:
            raise ProtocolError("resume source phase result changed while it was being copied")
        if (
            sha256_file(inherited_validation)
            != resume_state["previous_validation_sha256"]
        ):
            raise ProtocolError("resume source phase validation changed while it was being copied")
        previous_result = inherited_result
        route_card_sha256 = resume_state["route_card_sha256"]
        if route_card_sha256 is not None:
            inherited_card = output_dir / "route_card.json"
            if (
                not inherited_card.is_file()
                or sha256_file(inherited_card) != route_card_sha256
            ):
                raise ProtocolError("locked route card was not inherited byte-for-byte")
        resume_context = {
            "checkpoint": resume_state["checkpoint_relative"],
            "source_run": resume_state["source_run_relative"],
            "source_result": resume_state["previous_result"].relative_to(root).as_posix(),
            "source_active_minutes": resume_state["source_active_research_seconds"] / 60.0,
        }
    prompt = render_prompt(
        root,
        task,
        run_id,
        worker,
        output_dir,
        iteration_policy,
        accumulated_active_seconds=0.0,
        previous_result=previous_result,
        rollout_strategy=validation_rollout_strategy,
        route_card_only=sealed_breadth and resume_state is None,
        route_card_sha256=route_card_sha256,
        resume_context=resume_context,
    )
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
        "research_mode": (
            "continuation_depth"
            if resume_state is not None
            else task.get("research_mode", "legacy")
        ),
        "context_policy": (
            {
                "mode": "full_history",
                "source_context_policy": task.get(
                    "context_policy", {"mode": "full_history"}
                ),
            }
            if resume_state is not None
            else task.get("context_policy", {"mode": "full_history"})
        ),
        "rollout_strategy": None if resume_state is not None else rollout_strategy,
        "repository_source_snapshot": repository_source_snapshot(root, task),
        "dependency_results": dependency_results,
        "allow_unmet_dependencies": allow_unmet_dependencies,
    }
    if resume_state is not None:
        invocation["execution_mode"] = "checkpoint_continuation"
        invocation["active_research_seconds"] = 0.0
        invocation["iteration_complete"] = False
        invocation["eligible_for_statement_only_breadth"] = False
        invocation["eligible_for_fanout"] = False
        invocation["eligible_for_complete_fanout"] = False
        invocation["resume_lineage"] = {
            "checkpoint": resume_state["checkpoint_relative"],
            "checkpoint_sha256": resume_state["checkpoint_sha256"],
            "source_task_id": task_id,
            "source_run_id": resume_state["source_invocation"]["run_id"],
            "source_run": resume_state["source_run_relative"],
            "source_worker": resume_state["source_invocation"].get("worker"),
            "source_invocation_sha256": resume_state["source_invocation_sha256"],
            "source_task_snapshot_sha256": resume_state[
                "source_task_snapshot_sha256"
            ],
            "source_result": resume_state["previous_result"].relative_to(root).as_posix(),
            "source_result_sha256": resume_state["previous_result_sha256"],
            "inherited_result": inherited_result.relative_to(root).as_posix(),
            "inherited_validation": inherited_validation.relative_to(root).as_posix(),
            "inherited_validation_sha256": resume_state[
                "previous_validation_sha256"
            ],
            "source_phase": resume_state["previous_phase"]["phase"],
            "source_active_research_seconds": resume_state[
                "source_active_research_seconds"
            ],
            "credited_active_research_seconds": 0.0,
            "new_full_time_floor_required": True,
            "independence": False,
            "eligible_for_fanout": False,
            "counts_as_new_breadth": False,
            "validation_rollout_strategy": validation_rollout_strategy,
            "inherited_artifacts": inherited_records,
        }
        if route_card_sha256 is not None:
            invocation["route_card"] = {
                "path": (output_dir / "route_card.json").relative_to(root).as_posix(),
                "sha256": route_card_sha256,
                "staged_context": "inherited_locked_checkpoint",
                "source_path": resume_state["route_card_path"].relative_to(root).as_posix(),
            }
            invocation["route_card_sha256"] = route_card_sha256
    write_json(run_dir / "invocation.json", invocation)
    if dry_run:
        return run_dir

    minimum_active_seconds = 60.0 * iteration_policy["minimum_active_minutes_per_worker"]
    accumulated_active_seconds = 0.0
    phases: list[dict[str, Any]] = []
    phase = 0
    sealed_workspace: Path | None = None
    sealed_temporary: tempfile.TemporaryDirectory[str] | None = None
    if sealed_breadth and resume_state is None:
        # Keep the stage outside the Git worktree so Codex does not
        # automatically inherit the repository's ancestor AGENTS.md. This is
        # an intellectual-context control, not an OS security boundary.
        sealed_temporary = tempfile.TemporaryDirectory(prefix="rpcd-sealed-")
        sealed_workspace = Path(sealed_temporary.name).resolve()
        context = task.get("context_policy", {})
        allowed_inputs = context.get("allowlist") or task.get("inputs", [])[:1]
        for raw in allowed_inputs:
            source = (root / raw).resolve()
            destination = sealed_workspace / Path(*Path(raw).parts)
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
        sealed_metadata = {
            "schema_version": "1.0",
            "mode": context.get("mode"),
            "allowed_inputs": allowed_inputs,
            "limitation": (
                "The separate working directory reduces accidental history access, but is "
                "not an operating-system security boundary."
            ),
        }
        write_json(run_dir / "sealed-context.json", sealed_metadata)
        write_json(sealed_workspace / "sealed-context.json", sealed_metadata)
    events_dir = run_dir / "events"
    events_dir.mkdir()
    preflight_report = run_dir / "trusted_verifiers.preflight.json"

    def cleanup_sealed_workspace() -> None:
        nonlocal sealed_temporary, sealed_workspace
        if sealed_temporary is not None:
            sealed_temporary.cleanup()
            sealed_temporary = None
            sealed_workspace = None

    def execute_preflight() -> bool:
        verifier_records, verifier_errors = run_verifiers(
            task.get("verifiers", []),
            root=root,
            artifact_dir=output_dir,
            run_dir=run_dir,
            phase="preflight",
        )
        status = "passed" if verifier_records and not verifier_errors else (
            "failed" if verifier_errors else "not_configured"
        )
        write_json(
            preflight_report,
            {
                "schema_version": "1.0",
                "task_id": task_id,
                "run_id": run_id,
                "phase": "preflight",
                "status": status,
                "records": verifier_records,
                "errors": verifier_errors,
            },
        )
        invocation["preflight_verifiers"] = {
            "path": preflight_report.relative_to(root).as_posix(),
            "status": status,
            "valid": not verifier_errors,
        }
        write_json(run_dir / "invocation.json", invocation)
        if verifier_errors:
            invocation["iteration_complete"] = False
            invocation["preflight_failed"] = True
            write_json(run_dir / "invocation.json", invocation)
            write_json(
                run_dir / "incomplete_iteration.json",
                {
                    "reason": "trusted_preflight_failed",
                    "required_active_seconds": minimum_active_seconds,
                    "completed_active_seconds": accumulated_active_seconds,
                    "errors": verifier_errors,
                    "portable_checkpoint": True,
                },
            )
            raise ProtocolError(
                "trusted preflight failed before research: " + "; ".join(verifier_errors)
            )
        return bool(verifier_records)

    preflight_complete = False
    preflight_visible = False
    if not sealed_breadth or resume_state is not None:
        preflight_visible = execute_preflight()
        preflight_complete = True
    while True:
        phase += 1
        route_card_phase = sealed_breadth and route_card_sha256 is None
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
            rollout_strategy=validation_rollout_strategy,
            route_card_only=route_card_phase,
            route_card_sha256=route_card_sha256,
            preflight_report=(
                preflight_report if preflight_complete and preflight_visible else None
            ),
            resume_context=resume_context,
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
                    cwd=sealed_workspace if route_card_phase else root,
                    stdout=events,
                    stderr=errors,
                    check=False,
                )
        except OSError as error:
            cleanup_sealed_workspace()
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
            "phase_kind": "sealed_route_card" if route_card_phase else "research",
        }
        phases.append(phase_record)
        invocation["phases"] = phases
        invocation["active_research_seconds"] = accumulated_active_seconds
        invocation["iteration_complete"] = False
        write_json(run_dir / "invocation.json", invocation)

        if completed.returncode != 0:
            cleanup_sealed_workspace()
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
            cleanup_sealed_workspace()
            raise ProtocolError(f"Codex phase {phase} completed without producing a result")
        # A continuation pass receives the previous structured result and all common artifacts.
        # The final pass is required to report the iteration cumulatively.
        previous_result = phase_result

        if route_card_phase:
            assert sealed_workspace is not None
            staged_card = sealed_workspace / "route_card.json"
            route_card_errors: list[str] = []
            if not staged_card.is_file():
                route_card_errors.append("sealed route-card phase did not create route_card.json")
            else:
                try:
                    card = read_json(staged_card)
                    route_card_errors.extend(
                        validate_route_card(
                            card,
                            task=task,
                            rollout_strategy=validation_rollout_strategy,
                        )
                    )
                except ProtocolError as error:
                    route_card_errors.append(str(error))
            if not route_card_errors:
                locked_card = output_dir / "route_card.json"
                shutil.copy2(staged_card, locked_card)
                route_card_sha256 = sha256_file(locked_card)
                invocation["route_card"] = {
                    "path": locked_card.relative_to(root).as_posix(),
                    "sha256": route_card_sha256,
                    "staged_context": "external_ephemeral",
                    "staged_context_record": (
                        (run_dir / "sealed-context.json").relative_to(root).as_posix()
                    ),
                }
                # Persist the top-level lock hash immediately so a checkpoint
                # taken before the post-reveal pass can be resumed safely.
                invocation["route_card_sha256"] = route_card_sha256
            write_json(
                run_dir / f"phase-{phase:03d}-validation.json",
                {
                    "valid": not route_card_errors,
                    "minimum_active_time_reached": (
                        accumulated_active_seconds + 1e-6 >= minimum_active_seconds
                    ),
                    "errors": route_card_errors,
                },
            )
            write_json(run_dir / "invocation.json", invocation)
            if route_card_errors:
                cleanup_sealed_workspace()
                raise ProtocolError(
                    "sealed route card failed validation: " + "; ".join(route_card_errors)
                )
            cleanup_sealed_workspace()
            preflight_visible = execute_preflight()
            preflight_complete = True
            # A sealed breadth worker must get at least one post-reveal research pass,
            # even if the route-card subprocess itself consumed the two-hour floor.
            continue

        phase_result_value = read_json(phase_result)
        phase_errors = validate_result(
            phase_result_value,
            task=task,
            root=root,
            iteration_policy=iteration_policy,
            rollout_strategy=validation_rollout_strategy,
            active_seconds=(
                accumulated_active_seconds
                if accumulated_active_seconds + 1e-6 >= minimum_active_seconds
                else None
            ),
        )
        resolved_output = output_dir.resolve()
        if route_card_sha256 is not None:
            locked_card = output_dir / "route_card.json"
            if not locked_card.is_file() or sha256_file(locked_card) != route_card_sha256:
                phase_errors.append("immutable route_card.json was modified after reveal")
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
    if route_card_sha256 is not None:
        invocation["route_card_sha256"] = route_card_sha256
    write_json(run_dir / "invocation.json", invocation)

    result = read_json(result_path)
    errors = validate_result(
        result,
        task=task,
        root=root,
        iteration_policy=iteration_policy,
        active_seconds=accumulated_active_seconds,
        rollout_strategy=validation_rollout_strategy,
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
    final_verifier_specs = list(task.get("verifiers", []))
    for index, raw in enumerate(task.get("dynamic_verifier_artifacts", []), start=1):
        final_verifier_specs.append(
            {
                "name": f"agent-produced exact control {index}: {raw}",
                "command": ["{python}", f"{{artifact_dir}}/{raw}"],
                "mode": "exact",
                "timeout_seconds": 600,
                "expected_exit_code": 0,
                "when": "final",
            }
        )
    verifier_records, verifier_errors = run_verifiers(
        final_verifier_specs,
        root=root,
        artifact_dir=output_dir,
        run_dir=run_dir,
        phase="final",
    )
    write_json(
        run_dir / "trusted_verifiers.json",
        {
            "schema_version": "1.0",
            "task_id": task_id,
            "run_id": run_id,
            "records": verifier_records,
            "errors": verifier_errors,
        },
    )
    errors.extend(verifier_errors)
    write_json(run_dir / "validation.json", {"valid": not errors, "errors": errors})
    if errors:
        invocation["iteration_complete"] = False
        invocation["verification_failed"] = True
        write_json(run_dir / "invocation.json", invocation)
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
