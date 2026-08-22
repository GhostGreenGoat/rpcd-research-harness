"""Command-line entry point for the portable RPCD harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .artifacts import create_bundle, unpack_bundle, verify_bundle
from .codex_adapter import run_codex_task
from .protocol import (
    ProtocolError,
    audit_claim_ledger,
    checkpoint_run,
    claim_task,
    find_root,
    load_iteration_policy,
    list_tasks,
    load_task,
    read_json,
    validate_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rpcd-harness", description="Portable RPCD research harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="list research tasks")

    show = subparsers.add_parser("show", help="show a task JSON")
    show.add_argument("task_id")

    claim = subparsers.add_parser("claim", help="create or renew an advisory task claim")
    claim.add_argument("task_id")
    claim.add_argument("--worker", required=True)
    claim.add_argument("--hours", type=int, default=24)

    run = subparsers.add_parser("run-codex", help="run a task using the local Codex CLI")
    run.add_argument("task_id")
    run.add_argument("--worker", required=True)
    run.add_argument("--codex", default="codex")
    run.add_argument("--model")
    run.add_argument("--dry-run", action="store_true")

    validate = subparsers.add_parser("validate-result", help="validate a structured result")
    validate.add_argument("result", type=Path)
    validate.add_argument("--task-id")

    checkpoint = subparsers.add_parser("checkpoint", help="hash a completed or partial run")
    checkpoint.add_argument("task_id")
    checkpoint.add_argument("--run-dir", required=True, type=Path)

    subparsers.add_parser("audit-ledger", help="check claim statuses against promotion gates")

    pack = subparsers.add_parser("pack", help="create a credential-free portable work packet")
    pack.add_argument("task_id")
    pack.add_argument("--out", required=True, type=Path)
    pack.add_argument("--include-runs", action="store_true")

    verify = subparsers.add_parser("verify-bundle", help="verify a work packet manifest")
    verify.add_argument("bundle", type=Path)

    unpack = subparsers.add_parser("unpack", help="verify and unpack a work packet")
    unpack.add_argument("bundle", type=Path)
    unpack.add_argument("--dest", required=True, type=Path)
    unpack.add_argument("--force", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = find_root()
        if args.command == "list":
            for task in list_tasks(root):
                dependencies = ",".join(task["dependencies"]) or "-"
                print(
                    f"{task['task_id']:<32} {task['status']:<8} "
                    f"role={task['role']:<15} max={task['allowed_max_evidence']} deps={dependencies}"
                )
        elif args.command == "show":
            print(json.dumps(load_task(root, args.task_id), ensure_ascii=False, indent=2))
        elif args.command == "claim":
            if args.hours < 1:
                raise ProtocolError("--hours must be positive")
            print(claim_task(root, args.task_id, args.worker, args.hours))
        elif args.command == "run-codex":
            run_dir = run_codex_task(
                root,
                args.task_id,
                worker=args.worker,
                codex=args.codex,
                model=args.model,
                dry_run=args.dry_run,
            )
            print(run_dir)
        elif args.command == "validate-result":
            result = read_json(args.result)
            task = load_task(root, args.task_id or result.get("task_id", ""))
            invocation_path = args.result.parent / "invocation.json"
            active_seconds = None
            if invocation_path.is_file():
                invocation = read_json(invocation_path)
                active_seconds = invocation.get("active_research_seconds")
            errors = validate_result(
                result,
                task=task,
                iteration_policy=load_iteration_policy(root),
                active_seconds=active_seconds,
            )
            if active_seconds is None:
                errors.append(
                    "missing harness-owned active_research_seconds in sibling invocation.json"
                )
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("valid")
        elif args.command == "checkpoint":
            print(checkpoint_run(root, args.task_id, args.run_dir))
        elif args.command == "audit-ledger":
            errors = audit_claim_ledger(root)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("claim ledger is consistent")
        elif args.command == "pack":
            print(create_bundle(root, args.task_id, args.out, include_runs=args.include_runs))
        elif args.command == "verify-bundle":
            manifest = verify_bundle(args.bundle)
            print(
                json.dumps(
                    {
                        "valid": True,
                        "task_id": manifest["task_id"],
                        "files": len(manifest["files"]),
                        "include_runs": manifest["include_runs"],
                    },
                    indent=2,
                )
            )
        elif args.command == "unpack":
            written = unpack_bundle(args.bundle, args.dest, force=args.force)
            print(f"wrote {len(written)} files to {args.dest.resolve()}")
        else:
            parser.error(f"unknown command: {args.command}")
    except ProtocolError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
