from __future__ import annotations

import unittest
from fractions import Fraction
from itertools import permutations

import numpy as np

from scripts.iter4_adjacency_bessel import (
    adjacency_certificate,
    exact_block_feature_gram,
    orders_and_features,
)
from scripts.iter4_duplicate_child_counterexample import exact_record
from scripts.iter4_half_depth_scalar_induction_barrier import (
    exact_record as half_depth_barrier_record,
)
from scripts.iter4_root_t080_counterexample_audit import (
    exact_record as t080_counterexample_record,
)
from scripts.iter4_t095_bare_jensen_half_barrier import equicorrelation_parallel
from scripts.iter4_t095_reverse_pair_half_barrier import (
    exact_record as reverse_pair_barrier_record,
)


class PermutationBlockBesselTests(unittest.TestCase):
    def test_bare_jensen_cannot_prove_the_global_half_constant(self) -> None:
        record = equicorrelation_parallel(21, Fraction(9, 20))
        self.assertEqual(record["gap_to_one_half"], Fraction(-1, 12802))
        self.assertEqual(record["loewner_margin"], Fraction(-3, 800))

    def test_reverse_pairs_cannot_prove_the_global_half_constant(self) -> None:
        record = reverse_pair_barrier_record()
        self.assertEqual(record["reverse_pair_kernel_quotient"], Fraction(3, 8))
        self.assertEqual(record["gap_to_one_half"], Fraction(-1, 8))

    def test_duplicate_child_lemma_has_exact_counterexample(self) -> None:
        record = exact_record()
        self.assertEqual(record["value"], "7204453277/2441406250")
        self.assertEqual(record["gap_to_three"], "-119765473/2441406250")

    def test_half_depth_scalar_induction_fails_before_target_does(self) -> None:
        record = half_depth_barrier_record()
        self.assertEqual(
            record["cleared_induction_residual_transverse_eigenvalue"], "-28/225"
        )
        self.assertEqual(
            record["actual_J2_minus_2mu_over_m_Binverse_transverse_eigenvalue"],
            "12/25",
        )

    def test_t080_and_strong_one_epoch_have_exact_counterexample(self) -> None:
        record = t080_counterexample_record()
        self.assertTrue(record["boundary"]["gap_to_two"].startswith("-"))
        self.assertFalse(
            record["finite_positive_definite_ray"]["rate_minus_q"].startswith("-")
        )

    def test_exact_block_gram_matches_permutation_enumeration(self) -> None:
        n = 5
        blocks = [()] + [
            block
            for length in (2, 3)
            for block in permutations(range(n), length)
        ]
        block_index = {block: index for index, block in enumerate(blocks)}
        empirical = np.zeros((len(blocks), len(blocks)))
        orders = list(permutations(range(n)))
        for order in orders:
            active = [0]
            for length in (2, 3):
                active.extend(
                    block_index[order[start : start + length]]
                    for start in range(n - length + 1)
                )
            empirical[np.ix_(active, active)] += 1.0
        empirical /= len(orders)
        np.testing.assert_allclose(
            exact_block_feature_gram(n, blocks), empirical, atol=2e-15, rtol=2e-15
        )

    def test_bessel_hierarchy_and_rank_one_formula(self) -> None:
        n = 5
        correlation = np.ones((n, n))
        certificates = []
        exact = None
        generator = np.random.default_rng(7)
        for depth in (2, 3):
            orders, active, gram_inverse, feature_count = orders_and_features(
                n, depth, 0, generator
            )
            certificate, exact_value = adjacency_certificate(
                correlation,
                orders,
                active,
                gram_inverse,
                feature_count,
                False,
            )
            certificates.append(certificate)
            exact = exact_value
        assert exact is not None
        projector = np.eye(n) - np.ones((n, n)) / n
        expected = 2.0 * projector + np.eye(n) / n
        np.testing.assert_allclose(certificates[0], expected, atol=3e-14, rtol=3e-14)
        np.testing.assert_allclose(exact, expected, atol=3e-14, rtol=3e-14)
        self.assertGreaterEqual(
            np.linalg.eigvalsh(certificates[1] - certificates[0])[0], -3e-14
        )


if __name__ == "__main__":
    unittest.main()
