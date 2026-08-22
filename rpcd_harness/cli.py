"""Command-line entry point for the portable RPCD harness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .artifacts import create_bundle, unpack_bundle, verify_bundle
from .breadth import BreadthError, compute_effective_breadth, load_breadth_snapshot
from .codex_adapter import run_codex_task
from .fanout import merge_fanout_shards, run_fanout
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
from .routes import (
    RouteError,
    audit_route_repository,
    load_portfolio_policy,
    load_route_nodes,
    plan_route_allocation,
    prune_route,
    import_continuation_result,
    import_route_card,
    recommend_route,
    review_route_target,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rpcd-harness", description="Portable RPCD research harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    task_list = subparsers.add_parser("list", help="list research tasks")
    task_list.add_argument(
        "--frontier",
        action="store_true",
        help="show only live tasks attached to the current RPCD route portfolio",
    )

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
    run.add_argument("--allow-unmet-dependencies", action="store_true")
    run.add_argument(
        "--resume-from-checkpoint",
        type=Path,
        help=(
            "start a new continuation-depth run from a verified incomplete checkpoint; "
            "the new run receives no inherited active-time or breadth credit"
        ),
    )

    fanout = subparsers.add_parser(
        "fanout", help="launch independent RPCD route rollouts from a strategy manifest"
    )
    fanout.add_argument("task_id")
    fanout.add_argument("--manifest", required=True, type=Path)
    fanout.add_argument("--codex", default="codex")
    fanout.add_argument("--model")
    fanout.add_argument("--max-parallel", type=int, default=4)
    fanout.add_argument(
        "--rollout-id",
        action="append",
        dest="rollout_ids",
        help="run only this manifest rollout; repeat for a multi-rollout shard",
    )
    fanout.add_argument("--dry-run", action="store_true")

    fanout_merge = subparsers.add_parser(
        "fanout-merge",
        help="validate and merge transported rollout shards into one complete ensemble",
    )
    fanout_merge.add_argument("task_id")
    fanout_merge.add_argument("--manifest", required=True, type=Path)
    fanout_merge.add_argument(
        "--shard",
        required=True,
        action="extend",
        nargs="+",
        type=Path,
        help="one or more repository-relative shard ensemble.json paths; option may repeat",
    )

    validate = subparsers.add_parser("validate-result", help="validate a structured result")
    validate.add_argument("result", type=Path)
    validate.add_argument("--task-id")

    checkpoint = subparsers.add_parser("checkpoint", help="hash a completed or partial run")
    checkpoint.add_argument("task_id")
    checkpoint.add_argument("--run-dir", required=True, type=Path)

    subparsers.add_parser("audit-ledger", help="check claim statuses against promotion gates")
    subparsers.add_parser("route-list", help="list mathematical route-DAG nodes and recommendations")
    subparsers.add_parser("route-audit", help="validate the RPCD route DAG and breadth portfolio")
    route_plan = subparsers.add_parser(
        "route-plan",
        help="apply breadth gates, then rank eligible deepest RPCD frontier routes",
    )
    route_plan.add_argument(
        "--breadth-snapshot",
        type=Path,
        help="include a complete reviewer-declared active-frontier B_eff snapshot",
    )

    route_recommend = subparsers.add_parser(
        "route-recommend", help="score one RPCD route for deepen/scout/suspend"
    )
    route_recommend.add_argument("route_id")

    route_import = subparsers.add_parser(
        "route-import-card",
        help="import a validated Agent-generated sealed card into the route DAG",
    )
    route_import.add_argument("card", type=Path)
    route_import.add_argument("--route-id", required=True)

    route_import_depth = subparsers.add_parser(
        "route-import-continuation",
        help="import one validated continuation result as a proposed adjacent child",
    )
    route_import_depth.add_argument("result", type=Path)
    route_import_depth.add_argument("--avenue-index", type=int, default=0)

    route_review = subparsers.add_parser(
        "route-review-target",
        help="apply an independent RPCD target-fidelity review to a proposed route",
    )
    route_review.add_argument("route_id")
    route_review.add_argument("review", type=Path)

    route_prune = subparsers.add_parser(
        "route-prune",
        help="hard-prune a route from an independent E2+ exact/certified verdict",
    )
    route_prune.add_argument("route_id")
    route_prune.add_argument("verdict", type=Path)

    route_breadth = subparsers.add_parser(
        "route-breadth",
        help="compute reviewer-declared effective breadth for active frontier routes",
    )
    route_breadth.add_argument("snapshot", type=Path)

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
            tasks = list_tasks(root)
            if args.frontier:
                tasks = [
                    task
                    for task in tasks
                    if task.get("route_ids") and task.get("status") != "done"
                ]
            for task in tasks:
                dependencies = ",".join(task["dependencies"]) or "-"
                mode = task.get("research_mode", "legacy")
                print(
                    f"{task['task_id']:<32} {task['status']:<8} "
                    f"role={task['role']:<15} mode={mode:<18} "
                    f"max={task['allowed_max_evidence']} deps={dependencies}"
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
                allow_unmet_dependencies=args.allow_unmet_dependencies,
                resume_from_checkpoint=args.resume_from_checkpoint,
            )
            print(run_dir)
        elif args.command == "fanout":
            print(
                run_fanout(
                    root,
                    args.task_id,
                    args.manifest,
                    codex=args.codex,
                    model=args.model,
                    max_parallel=args.max_parallel,
                    dry_run=args.dry_run,
                    rollout_ids=args.rollout_ids,
                )
            )
        elif args.command == "fanout-merge":
            print(
                merge_fanout_shards(
                    root,
                    args.task_id,
                    args.manifest,
                    args.shard,
                )
            )
        elif args.command == "validate-result":
            result = read_json(args.result)
            task = load_task(root, args.task_id or result.get("task_id", ""))
            invocation_path = args.result.parent / "invocation.json"
            active_seconds = None
            rollout_strategy = None
            if invocation_path.is_file():
                invocation = read_json(invocation_path)
                active_seconds = invocation.get("active_research_seconds")
                rollout_strategy = invocation.get("rollout_strategy")
            errors = validate_result(
                result,
                task=task,
                root=root,
                iteration_policy=load_iteration_policy(root),
                active_seconds=active_seconds,
                rollout_strategy=rollout_strategy,
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
        elif args.command == "route-list":
            policy = load_portfolio_policy(root)
            tasks = list_tasks(root)
            for route in load_route_nodes(root):
                recommendation = recommend_route(route, policy)
                linked_tasks = ",".join(
                    task["task_id"] for task in tasks if route["route_id"] in task.get("route_ids", [])
                ) or "-"
                print(
                    f"{route['route_id']:<38} {route['layer']:<2} "
                    f"{route['status']:<9} next={recommendation:<7} "
                    f"family={route['method_family']} tasks={linked_tasks}"
                )
        elif args.command == "route-audit":
            errors = audit_route_repository(root)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
            print("route DAG and active RPCD breadth portfolio are consistent")
        elif args.command == "route-plan":
            routes = load_route_nodes(root)
            effective_breadth = None
            breadth_review_kind = None
            if args.breadth_snapshot is not None:
                breadth_result = compute_effective_breadth(
                    load_breadth_snapshot(args.breadth_snapshot),
                    routes=routes,
                )
                effective_breadth = breadth_result["effective_breadth"]
                breadth_review_kind = breadth_result["kind"]
            print(
                json.dumps(
                    plan_route_allocation(
                        routes,
                        load_portfolio_policy(root),
                        effective_breadth=effective_breadth,
                        breadth_review_kind=breadth_review_kind,
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        elif args.command == "route-recommend":
            routes = {route["route_id"]: route for route in load_route_nodes(root)}
            if args.route_id not in routes:
                raise ProtocolError(f"unknown route id: {args.route_id}")
            print(recommend_route(routes[args.route_id], load_portfolio_policy(root)))
        elif args.command == "route-import-card":
            print(import_route_card(root, args.card, args.route_id))
        elif args.command == "route-import-continuation":
            print(
                import_continuation_result(
                    root, args.result, avenue_index=args.avenue_index
                )
            )
        elif args.command == "route-review-target":
            print(review_route_target(root, args.route_id, args.review))
        elif args.command == "route-prune":
            print(prune_route(root, args.route_id, args.verdict))
        elif args.command == "route-breadth":
            print(
                json.dumps(
                    compute_effective_breadth(
                        load_breadth_snapshot(args.snapshot),
                        routes=load_route_nodes(root),
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )
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
    except (ProtocolError, RouteError, BreadthError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
