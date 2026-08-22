from __future__ import annotations

import unittest

from rpcd_harness.protocol import (
    audit_claim_ledger,
    find_root,
    list_tasks,
    load_iteration_policy,
    validate_result,
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


class ProtocolTests(unittest.TestCase):
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

    def test_all_tasks_are_well_formed(self) -> None:
        root = find_root()
        tasks = list_tasks(root)
        self.assertGreaterEqual(len(tasks), 8)

    def test_ledger_is_consistent(self) -> None:
        self.assertEqual(audit_claim_ledger(find_root()), [])

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

    def test_artifact_path_cannot_escape_repo(self) -> None:
        result = base_result()
        result["artifacts"] = [
            {"path": "../secret", "kind": "data", "description": "bad"}
        ]
        errors = validate_result(result)
        self.assertTrue(any("unsafe relative path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
