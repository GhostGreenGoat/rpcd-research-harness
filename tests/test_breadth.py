from __future__ import annotations

import unittest

from rpcd_harness.breadth import BreadthError, compute_effective_breadth


def snapshot(similarity: float) -> dict:
    return {
        "schema_version": "1.0",
        "snapshot_id": "test-width",
        "kind": "planning_estimate",
        "reviewer": "test-reviewer",
        "created_at": "2026-08-22T00:00:00Z",
        "entries": [
            {"route_id": "R110", "weight": 1},
            {"route_id": "R120", "weight": 1},
        ],
        "similarities": [
            {"route_a": "R110", "route_b": "R110", "value": 1, "rationale": "same route"},
            {
                "route_a": "R110",
                "route_b": "R120",
                "value": similarity,
                "rationale": "reviewed method overlap",
            },
            {"route_a": "R120", "route_b": "R120", "value": 1, "rationale": "same route"},
        ],
        "limitations": ["This is a portfolio diagnostic, not proof confidence."],
    }


class EffectiveBreadthTests(unittest.TestCase):
    def test_independent_and_duplicate_routes_have_expected_width(self) -> None:
        self.assertAlmostEqual(compute_effective_breadth(snapshot(0))["effective_breadth"], 2)
        self.assertAlmostEqual(compute_effective_breadth(snapshot(1))["effective_breadth"], 1)

    def test_missing_pair_and_nonunit_diagonal_are_rejected(self) -> None:
        value = snapshot(0.5)
        value["similarities"] = value["similarities"][:-1]
        with self.assertRaisesRegex(BreadthError, "missing similarity pairs"):
            compute_effective_breadth(value)
        value = snapshot(0.5)
        value["similarities"][0]["value"] = 0.9
        with self.assertRaisesRegex(BreadthError, "must equal one"):
            compute_effective_breadth(value)

    def test_snapshot_must_cover_the_complete_active_frontier(self) -> None:
        routes = [
            {"route_id": route_id, "status": "active", "layer": "L1", "parent_ids": []}
            for route_id in ("R110", "R120", "R130")
        ]
        with self.assertRaisesRegex(BreadthError, "omits active frontier routes: R130"):
            compute_effective_breadth(snapshot(0.5), routes=routes)


if __name__ == "__main__":
    unittest.main()
