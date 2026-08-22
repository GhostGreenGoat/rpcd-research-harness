from __future__ import annotations

import unittest
from pathlib import Path

from rpcd_harness.protocol import find_root, load_task, validate_result


TASK_IDS = (
    "T145-fresh-reconstruct-audited-route",
    "T146-novelty-audit-audited-route",
    "T147-formal-exact-human-handoff",
)


def route_lemma_refutation(task_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "task_id": task_id,
        "run_id": "run-hostile-route-label",
        "worker": "hostile-fixture",
        "status": "partial",
        "summary": "A sufficient route lemma failed; the master claim was not tested.",
        "claims": [
            {
                "claim_id": "C050",
                "statement": "Selected route lemma has a counterexample",
                "statement_ref": "research/problem.md#current-finite-time-target",
                "status": "refuted",
                "evidence_level": "E2",
                "assumptions": [],
                "supporting_artifacts": [],
                "open_objections": [],
            }
        ],
        "artifacts": [],
        "checks": [],
        "failed_attempts": ["the selected sufficient lemma failed"],
        "iteration": {
            "avenues": [
                {
                    "name": "route lemma witness",
                    "objective": "check the local sufficient lemma",
                    "outcome": "local failure",
                    "status": "refuted",
                },
                {
                    "name": "canonical quantifier audit",
                    "objective": "compare the witness with the full G-FT negation",
                    "outcome": "the witness does not negate C050",
                    "status": "completed",
                },
                {
                    "name": "claim identity audit",
                    "objective": "keep local and master statements separate",
                    "outcome": "the attempted C050 label is invalid",
                    "status": "completed",
                },
            ],
            "checkpoints": [],
            "stress_tests": ["canonical statement comparison"],
            "deepest_obstruction": "route-local failure does not refute G-FT",
        },
        "literature": [],
        "next_tasks": [],
        "limitations": ["No witness to the full canonical C050 negation."],
    }


class FollowupTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = find_root()
        cls.tasks = {task_id: load_task(cls.root, task_id) for task_id in TASK_IDS}

    def test_roles_evidence_ceilings_and_validated_dependency_chain(self) -> None:
        expected = {
            "T145-fresh-reconstruct-audited-route": (
                "reproducer",
                "E5",
                ["T144-audit-sealed-finite-time-route"],
            ),
            "T146-novelty-audit-audited-route": (
                "librarian",
                "E2",
                ["T144-audit-sealed-finite-time-route"],
            ),
            "T147-formal-exact-human-handoff": (
                "formalizer",
                "E5",
                [
                    "T144-audit-sealed-finite-time-route",
                    "T145-fresh-reconstruct-audited-route",
                    "T146-novelty-audit-audited-route",
                ],
            ),
        }
        for task_id, (role, ceiling, dependencies) in expected.items():
            with self.subTest(task_id=task_id):
                task = self.tasks[task_id]
                self.assertEqual(task["role"], role)
                self.assertEqual(task["allowed_max_evidence"], ceiling)
                self.assertEqual(task["dependencies"], dependencies)
                self.assertEqual(task["dependency_mode"], "latest_validated_run")
                self.assertTrue(task["require_distinct_dependency_workers"])
                self.assertEqual(task["status"], "blocked")
        # These are prospective gates, so their static coordination records do
        # not pretend that any run has completed. Protocol regression tests
        # separately ensure that even a task-level done flag cannot replace a
        # concrete validated dependency run.
        for upstream in (
            "T144-audit-sealed-finite-time-route",
            "T145-fresh-reconstruct-audited-route",
            "T146-novelty-audit-audited-route",
        ):
            self.assertNotEqual(load_task(self.root, upstream)["status"], "done")

    def test_inputs_are_static_existing_files_not_dynamic_run_placeholders(self) -> None:
        forbidden_fragments = ("runs/", "<run", "{run", "latest-result")
        for task_id, task in self.tasks.items():
            with self.subTest(task_id=task_id):
                self.assertEqual(
                    task["context_policy"]["allowlist"], task["inputs"]
                )
                for raw in task["inputs"]:
                    normalized = raw.replace("\\", "/").lower()
                    self.assertFalse(
                        any(fragment in normalized for fragment in forbidden_fragments),
                        raw,
                    )
                    self.assertTrue((self.root / raw).exists(), raw)

    def test_correctness_reconstruction_and_novelty_are_separate_contracts(self) -> None:
        hostile_audit = load_task(
            self.root, "T144-audit-sealed-finite-time-route"
        )
        reconstruction = self.tasks["T145-fresh-reconstruct-audited-route"]
        novelty = self.tasks["T146-novelty-audit-audited-route"]
        handoff = self.tasks["T147-formal-exact-human-handoff"]
        reconstruction_contract = " ".join(
            [reconstruction["objective"], *reconstruction["acceptance_checks"]]
        ).lower()
        novelty_contract = " ".join(
            [novelty["objective"], *novelty["acceptance_checks"]]
        ).lower()
        handoff_contract = " ".join(
            [handoff["objective"], *handoff["acceptance_checks"]]
        ).lower()
        hostile_contract = " ".join(
            [hostile_audit["objective"], *hostile_audit["acceptance_checks"]]
        ).lower()

        self.assertEqual(hostile_audit["allowed_max_evidence"], "E4")
        self.assertIn("reconstruction_seed.json", hostile_audit["required_artifacts"])
        self.assertIn("proof-free frozen package", hostile_contract)
        self.assertIn("not the fresh e5 independent reconstruction", hostile_contract)
        self.assertIn("must not close or claim", hostile_contract)
        self.assertIn("hostile audit", reconstruction_contract)
        self.assertIn("not an independent reconstruction", reconstruction_contract)
        self.assertIn("statement-only exposure", reconstruction_contract)
        self.assertIn("withholds e5", reconstruction_contract)
        self.assertIn("correctness does not establish novelty", novelty_contract)
        self.assertIn("novelty does not establish correctness", novelty_contract)
        self.assertIn("kernel", handoff_contract)
        self.assertIn("finite statements only", handoff_contract)
        self.assertIn("qualified human", handoff_contract)

    def test_dynamic_exact_controls_are_required_and_executed_at_final(self) -> None:
        expected = {
            "T145-fresh-reconstruct-audited-route": "independent_controls.py",
            "T147-formal-exact-human-handoff": "exact_certificate.py",
        }
        for task_id, artifact in expected.items():
            with self.subTest(task_id=task_id):
                task = self.tasks[task_id]
                self.assertIn(artifact, task["required_artifacts"])
                self.assertIn(artifact, task["dynamic_verifier_artifacts"])

    def test_route_lemma_failure_cannot_be_reported_as_c050_refuted(self) -> None:
        for task_id, task in self.tasks.items():
            with self.subTest(task_id=task_id):
                self.assertTrue(task["strict_claim_scope"])
                self.assertTrue(task["strict_claim_binding"])
                self.assertFalse(task["may_refute_master_claim"])
                errors = validate_result(
                    route_lemma_refutation(task_id),
                    task=task,
                    root=Path(self.root),
                )
                self.assertTrue(
                    any("canonical claim title" in error for error in errors), errors
                )
                self.assertTrue(
                    any("not authorized" in error for error in errors), errors
                )


if __name__ == "__main__":
    unittest.main()
