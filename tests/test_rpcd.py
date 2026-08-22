from __future__ import annotations

import unittest
from itertools import permutations

import numpy as np

from rpcd_harness.rpcd import (
    conjectured_rate_bound,
    correlation_from_offdiagonal_direction,
    epoch_operator_factor,
    epoch_operator_product,
    exact_rpcd_rate,
    exact_one_epoch_energy_rate,
    factor_gram_beta,
    generalized_energy_rate,
    gram_determinant_rate_bound,
    identity_errors,
    inverse_minorant_polynomial,
    matrix_jensen_rate,
    normalize_unit_diagonal,
    random_correlation,
    resolvent_moment_upper_matrix,
    set_minimum_eigenvalue,
    spectral_floor_determinant_rate_bound,
    structured_hessian,
    strong_one_epoch_margin,
    two_step_projection_matrices,
    permutation_factor,
    projection_epoch_product,
)


class RpcdLinearAlgebraTests(unittest.TestCase):
    def test_normalization(self) -> None:
        raw = np.array([[4.0, 1.0], [1.0, 9.0]])
        normalized = normalize_unit_diagonal(raw)
        np.testing.assert_allclose(np.diag(normalized), np.ones(2), atol=1e-14)
        self.assertGreater(np.linalg.eigvalsh(normalized)[0], 0.0)

    def test_product_and_factor_forms_agree(self) -> None:
        matrix = set_minimum_eigenvalue(random_correlation(4, 13), 0.3)
        for order in permutations(range(4)):
            np.testing.assert_allclose(
                epoch_operator_product(matrix, order),
                epoch_operator_factor(matrix, order),
                atol=2e-13,
                rtol=2e-13,
            )

    def test_identity_hessian_converges_in_one_epoch(self) -> None:
        self.assertAlmostEqual(exact_rpcd_rate(np.eye(3)), 0.0, places=14)
        self.assertAlmostEqual(matrix_jensen_rate(np.eye(3)), 0.0, places=14)

    def test_candidate_identities(self) -> None:
        matrix = set_minimum_eigenvalue(random_correlation(4, 29), 0.45)
        errors = identity_errors(matrix)
        self.assertLess(errors["product_factor_max_abs"], 2e-12)
        self.assertLess(errors["energy_identity_max_abs"], 2e-12)
        self.assertLess(errors["expected_factor_gram_max_abs"], 2e-12)
        self.assertGreater(errors["jensen_residual_min_eigenvalue"], -2e-12)

    def test_structured_and_random_cases_obey_tested_bounds(self) -> None:
        cases = [
            structured_hessian(3, 0.2),
            structured_hessian(4, 0.7, [1, -1, 1, -1]),
            set_minimum_eigenvalue(random_correlation(3, 101), 0.35),
        ]
        for matrix in cases:
            with self.subTest(matrix=matrix.tolist()):
                rate = exact_rpcd_rate(matrix)
                sigma = float(np.linalg.eigvalsh(matrix)[0])
                self.assertLessEqual(rate, conjectured_rate_bound(matrix.shape[0], sigma) + 2e-10)
                self.assertLessEqual(rate, matrix_jensen_rate(matrix) + 2e-10)

    def test_raw_jensen_scalar_bound_does_not_always_imply_conjecture(self) -> None:
        matrix = np.array(
            [
                [1.0, -0.754, 0.816, -0.783],
                [-0.754, 1.0, -0.858, 0.771],
                [0.816, -0.858, 1.0, -0.696],
                [-0.783, 0.771, -0.696, 1.0],
            ]
        )
        target = conjectured_rate_bound(4, float(np.linalg.eigvalsh(matrix)[0]))
        self.assertGreater(matrix_jensen_rate(matrix) - target, 0.03)
        self.assertLess(exact_rpcd_rate(matrix), target)

    def test_resolvent_hierarchy_is_a_monotone_upper_bound(self) -> None:
        matrix = set_minimum_eigenvalue(random_correlation(4, 73), 0.2)
        exact_energy = exact_one_epoch_energy_rate(matrix)
        upper_one = resolvent_moment_upper_matrix(matrix, level=1)
        upper_two = resolvent_moment_upper_matrix(matrix, level=2)
        rate_one = generalized_energy_rate(matrix, upper_one)
        rate_two = generalized_energy_rate(matrix, upper_two)
        self.assertGreaterEqual(rate_one + 2e-11, rate_two)
        self.assertGreaterEqual(rate_two + 2e-11, exact_energy)

        order = (2, 0, 3, 1)
        factor = permutation_factor(matrix, order)
        x = factor @ factor.T
        beta = factor_gram_beta(matrix)
        residual = np.linalg.inv(x) - inverse_minorant_polynomial(x, level=2, scale=beta)
        self.assertGreater(np.linalg.eigvalsh((residual + residual.T) / 2.0)[0], -2e-12)

    def test_two_step_without_replacement_has_psd_advantage(self) -> None:
        matrix = set_minimum_eigenvalue(random_correlation(5, 83), 0.3)
        with_replacement, without_replacement, difference = two_step_projection_matrices(matrix)
        np.testing.assert_allclose(
            with_replacement - without_replacement,
            difference,
            atol=2e-13,
            rtol=2e-13,
        )
        self.assertGreater(np.linalg.eigvalsh((difference + difference.T) / 2.0)[0], -2e-12)

    def test_projection_defect_has_gram_determinant(self) -> None:
        matrix = set_minimum_eigenvalue(random_correlation(4, 97), 0.35)
        determinant = np.linalg.det(matrix)
        rate_bound = gram_determinant_rate_bound(matrix)
        for order in permutations(range(4)):
            product = projection_epoch_product(matrix, order)
            defect = np.eye(4) - product.T @ product
            self.assertAlmostEqual(np.linalg.det(defect), determinant, places=11)
            self.assertLessEqual(np.linalg.norm(product, 2) ** 2, rate_bound + 2e-12)

    def test_determinant_bound_proves_the_two_dimensional_target(self) -> None:
        for sigma in (0.05, 0.2, 0.5, 0.9, 1.0):
            bound = spectral_floor_determinant_rate_bound(2, sigma)
            self.assertLessEqual(bound, conjectured_rate_bound(2, sigma) + 2e-14)

    def test_fixed_sigma_direction_parameterization(self) -> None:
        direction = np.array(
            [
                [0.0, -2.0, 0.5, 1.0],
                [-2.0, 0.0, -1.0, 0.25],
                [0.5, -1.0, 0.0, 1.5],
                [1.0, 0.25, 1.5, 0.0],
            ]
        )
        matrix = correlation_from_offdiagonal_direction(direction, 0.17)
        np.testing.assert_allclose(np.diag(matrix), np.ones(4), atol=2e-14)
        self.assertAlmostEqual(np.linalg.eigvalsh(matrix)[0], 0.17, places=13)

    def test_structured_family_satisfies_strong_one_epoch_target(self) -> None:
        for n in (2, 3, 4):
            for sigma in (0.1, 0.4, 0.8):
                matrix = structured_hessian(n, sigma)
                self.assertGreaterEqual(strong_one_epoch_margin(matrix), -2e-12)

    def test_orbit_midpoint_can_reduce_the_rpcd_rate_at_fixed_sigma(self) -> None:
        matrix = structured_hessian(3, 0.4, [1, -1, -1])
        swap = np.eye(3)[[1, 0, 2], :]
        midpoint = (matrix + swap.T @ matrix @ swap) / 2.0
        self.assertAlmostEqual(np.linalg.eigvalsh(matrix)[0], 0.4, places=13)
        self.assertAlmostEqual(np.linalg.eigvalsh(midpoint)[0], 0.4, places=13)
        expected_structured = (4521.0 + 3.0 * np.sqrt(2321049.0)) / 31250.0
        expected_midpoint = 153.0 / 625.0
        self.assertAlmostEqual(exact_rpcd_rate(matrix), expected_structured, places=12)
        self.assertAlmostEqual(exact_rpcd_rate(midpoint), expected_midpoint, places=12)
        self.assertGreater(exact_rpcd_rate(matrix), exact_rpcd_rate(midpoint))


if __name__ == "__main__":
    unittest.main()
