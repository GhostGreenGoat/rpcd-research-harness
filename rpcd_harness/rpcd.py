"""Deterministic linear-algebra primitives for RPCD on quadratic objectives.

The routines in this module use exhaustive permutation enumeration.  They are
therefore intended for small dimensions and verifier construction, not for
large-scale optimization.  Floating-point eigenvalue calculations remain
numerical evidence even when every permutation is enumerated.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import factorial
from typing import Iterable, Iterator, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatMatrix = NDArray[np.float64]


@dataclass(frozen=True)
class MatrixDiagnostics:
    dimension: int
    symmetry_error: float
    diagonal_error: float
    min_eigenvalue: float
    max_eigenvalue: float


def _matrix(value: ArrayLike) -> FloatMatrix:
    matrix = np.asarray(value, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("expected a square matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("matrix contains a non-finite entry")
    return matrix


def matrix_diagnostics(a: ArrayLike) -> MatrixDiagnostics:
    matrix = _matrix(a)
    symmetric = (matrix + matrix.T) / 2.0
    eigenvalues = np.linalg.eigvalsh(symmetric)
    return MatrixDiagnostics(
        dimension=matrix.shape[0],
        symmetry_error=float(np.max(np.abs(matrix - matrix.T))),
        diagonal_error=float(np.max(np.abs(np.diag(matrix) - 1.0))),
        min_eigenvalue=float(eigenvalues[0]),
        max_eigenvalue=float(eigenvalues[-1]),
    )


def validate_unit_diagonal_spd(a: ArrayLike, tolerance: float = 1e-10) -> FloatMatrix:
    matrix = _matrix(a)
    diagnostics = matrix_diagnostics(matrix)
    if diagnostics.symmetry_error > tolerance:
        raise ValueError(f"matrix is not symmetric within tolerance: {diagnostics.symmetry_error}")
    if diagnostics.diagonal_error > tolerance:
        raise ValueError(f"matrix is not unit diagonal within tolerance: {diagnostics.diagonal_error}")
    if diagnostics.min_eigenvalue <= tolerance:
        raise ValueError(f"matrix is not safely positive definite: {diagnostics.min_eigenvalue}")
    return (matrix + matrix.T) / 2.0


def normalize_unit_diagonal(a: ArrayLike) -> FloatMatrix:
    """Symmetrize and diagonally scale an SPD matrix to a correlation matrix."""
    matrix = _matrix(a)
    matrix = (matrix + matrix.T) / 2.0
    diagonal = np.diag(matrix)
    if np.any(diagonal <= 0.0):
        raise ValueError("positive diagonal required for normalization")
    inverse_sqrt = np.diag(1.0 / np.sqrt(diagonal))
    return inverse_sqrt @ matrix @ inverse_sqrt


def coordinate_update_operator(a: ArrayLike, coordinate: int) -> FloatMatrix:
    """Return U_i = I - e_i e_i^T A for a unit-diagonal Hessian."""
    matrix = _matrix(a)
    n = matrix.shape[0]
    if coordinate < 0 or coordinate >= n:
        raise IndexError(coordinate)
    update = np.eye(n)
    update[coordinate, :] -= matrix[coordinate, :]
    return update


def epoch_operator_product(a: ArrayLike, order: Sequence[int]) -> FloatMatrix:
    """Compose coordinate updates in the given chronological order."""
    matrix = _matrix(a)
    n = matrix.shape[0]
    if tuple(sorted(order)) != tuple(range(n)):
        raise ValueError("order must be a permutation of range(n)")
    transform = np.eye(n)
    for coordinate in order:
        transform = coordinate_update_operator(matrix, coordinate) @ transform
    return transform


def permutation_factor(a: ArrayLike, order: Sequence[int]) -> FloatMatrix:
    """Return the original-coordinate Gauss-Seidel factor M_p.

    If P has columns e_{p_1},...,e_{p_n}, then
    M_p = P tril(P^T A P) P^T and T_p = I - M_p^{-1} A.
    """
    matrix = _matrix(a)
    n = matrix.shape[0]
    if tuple(sorted(order)) != tuple(range(n)):
        raise ValueError("order must be a permutation of range(n)")
    permutation_matrix = np.eye(n)[:, list(order)]
    permuted = permutation_matrix.T @ matrix @ permutation_matrix
    return permutation_matrix @ np.tril(permuted) @ permutation_matrix.T


def epoch_operator_factor(a: ArrayLike, order: Sequence[int]) -> FloatMatrix:
    matrix = _matrix(a)
    factor = permutation_factor(matrix, order)
    return np.eye(matrix.shape[0]) - np.linalg.solve(factor, matrix)


def all_orders(n: int, max_dimension: int = 8) -> Iterator[tuple[int, ...]]:
    if n < 1:
        raise ValueError("dimension must be positive")
    if n > max_dimension:
        raise ValueError(
            f"refusing exhaustive enumeration for n={n}; max_dimension={max_dimension}"
        )
    return permutations(range(n))


def exact_second_moment_operator(a: ArrayLike, max_dimension: int = 8) -> FloatMatrix:
    r"""Return E[T_p \otimes T_p] by enumerating all n! permutations."""
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    accumulator = np.zeros((n * n, n * n), dtype=np.float64)
    for order in all_orders(n, max_dimension=max_dimension):
        transform = epoch_operator_factor(matrix, order)
        accumulator += np.kron(transform, transform)
    return accumulator / factorial(n)


def spectral_radius(matrix: ArrayLike) -> float:
    square = _matrix(matrix)
    eigenvalues = np.linalg.eigvals(square)
    return float(np.max(np.abs(eigenvalues)))


def exact_rpcd_rate(a: ArrayLike, max_dimension: int = 8) -> float:
    """Numerical Perron rate of the exhaustively averaged covariance map."""
    return spectral_radius(exact_second_moment_operator(a, max_dimension=max_dimension))


def conjectured_rate_bound(n: int, sigma: float) -> float:
    if n < 1:
        raise ValueError("dimension must be positive")
    if not (0.0 < sigma <= 1.0 + 1e-12):
        raise ValueError("sigma must lie in (0, 1]")
    return max((1.0 - 1.0 / n) ** n, (1.0 - sigma / n) ** (2 * n))


def matrix_jensen_s(a: ArrayLike) -> FloatMatrix:
    matrix = validate_unit_diagonal_spd(a)
    h = matrix - np.eye(matrix.shape[0])
    h_squared = h @ h
    return h_squared / 3.0 + np.diag(np.diag(h_squared)) / 6.0


def symmetric_inverse_sqrt(a: ArrayLike) -> FloatMatrix:
    matrix = _matrix(a)
    eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.T) / 2.0)
    if eigenvalues[0] <= 0.0:
        raise ValueError("positive definite matrix required")
    return (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T


def matrix_jensen_rate(a: ArrayLike) -> float:
    """Return theta/(1+theta) for the candidate A-energy contraction bound."""
    matrix = validate_unit_diagonal_spd(a)
    inverse_sqrt = symmetric_inverse_sqrt(matrix)
    scaled_s = inverse_sqrt @ matrix_jensen_s(matrix) @ inverse_sqrt
    theta = float(np.linalg.eigvalsh((scaled_s + scaled_s.T) / 2.0)[-1])
    if theta < -1e-12:
        raise ArithmeticError(f"unexpected negative theta: {theta}")
    theta = max(theta, 0.0)
    return theta / (1.0 + theta)


def expected_factor_gram(a: ArrayLike, max_dimension: int = 8) -> FloatMatrix:
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    accumulator = np.zeros_like(matrix)
    for order in all_orders(n, max_dimension=max_dimension):
        factor = permutation_factor(matrix, order)
        accumulator += factor @ factor.T
    return accumulator / factorial(n)


def expected_energy_pushforward(a: ArrayLike, max_dimension: int = 8) -> FloatMatrix:
    """Return E[T_p^T A T_p] by exhaustive enumeration."""
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    accumulator = np.zeros_like(matrix)
    for order in all_orders(n, max_dimension=max_dimension):
        transform = epoch_operator_factor(matrix, order)
        accumulator += transform.T @ matrix @ transform
    return accumulator / factorial(n)


def matrix_jensen_upper_matrix(a: ArrayLike) -> FloatMatrix:
    matrix = validate_unit_diagonal_spd(a)
    return matrix - matrix @ np.linalg.solve(matrix + matrix_jensen_s(matrix), matrix)


def factor_gram_beta(a: ArrayLike) -> float:
    """Common squared Frobenius norm of every permuted triangular factor."""
    matrix = validate_unit_diagonal_spd(a)
    return float((matrix.shape[0] + np.trace(matrix @ matrix)) / 2.0)


def inverse_minorant_polynomial(x: ArrayLike, level: int, scale: float) -> FloatMatrix:
    r"""Return p_{r,c}(X)=c^{-1} sum_{k=0}^{2r-1}(I-X/c)^k.

    For every SPD X, p_{r,c}(X) \preceq X^{-1}.  Odd truncation length is
    essential: the exact remainder is X^{-1}(I-X/c)^{2r}.
    """
    matrix = _matrix(x)
    if level < 1:
        raise ValueError("level must be positive")
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    remainder_base = np.eye(matrix.shape[0]) - matrix / scale
    power = np.eye(matrix.shape[0])
    polynomial = np.zeros_like(matrix)
    for _ in range(2 * level):
        polynomial += power
        power = power @ remainder_base
    return polynomial / scale


def resolvent_moment_upper_matrix(
    a: ArrayLike,
    level: int,
    scale: float | None = None,
    max_dimension: int = 8,
) -> FloatMatrix:
    """Finite-level analytic refinement of the bare matrix-Jensen upper bound."""
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    chosen_scale = factor_gram_beta(matrix) if scale is None else scale
    y = matrix + matrix_jensen_s(matrix)
    correction = np.zeros_like(matrix)
    for order in all_orders(n, max_dimension=max_dimension):
        factor = permutation_factor(matrix, order)
        x = factor @ factor.T
        delta = x - y
        correction += delta @ inverse_minorant_polynomial(x, level, chosen_scale) @ delta
    correction /= factorial(n)
    y_inverse_a = np.linalg.solve(y, matrix)
    return matrix - matrix @ y_inverse_a - matrix @ np.linalg.solve(y, correction) @ y_inverse_a


def generalized_energy_rate(a: ArrayLike, energy_matrix: ArrayLike) -> float:
    """Largest generalized eigenvalue of energy_matrix relative to A."""
    matrix = validate_unit_diagonal_spd(a)
    energy = _matrix(energy_matrix)
    if energy.shape != matrix.shape:
        raise ValueError("energy matrix has the wrong shape")
    inverse_sqrt = symmetric_inverse_sqrt(matrix)
    scaled = inverse_sqrt @ energy @ inverse_sqrt
    return float(np.linalg.eigvalsh((scaled + scaled.T) / 2.0)[-1])


def exact_one_epoch_energy_rate(a: ArrayLike, max_dimension: int = 8) -> float:
    return generalized_energy_rate(
        a,
        expected_energy_pushforward(a, max_dimension=max_dimension),
    )


def strong_one_epoch_margin(a: ArrayLike, max_dimension: int = 8) -> float:
    r"""Return ``q(n, sigma) - lambda_max(E[T^T A T], A)``.

    A negative value is a numerical counterexample candidate to the strong
    one-epoch A-energy inequality.  It is not by itself a counterexample to
    the asymptotic covariance-rate conjecture.
    """
    matrix = validate_unit_diagonal_spd(a)
    diagnostics = matrix_diagnostics(matrix)
    target = conjectured_rate_bound(matrix.shape[0], diagnostics.min_eigenvalue)
    return target - exact_one_epoch_energy_rate(matrix, max_dimension=max_dimension)


def correlation_from_offdiagonal_direction(
    direction: ArrayLike,
    sigma: float,
) -> FloatMatrix:
    r"""Map a zero-diagonal symmetric direction to the fixed-spectral-floor slice.

    If ``H`` is the symmetrized, zero-diagonal input, this returns
    ``A = I + alpha H`` with ``lambda_min(A) = sigma``.  Scaling ``H`` does
    not change the result.  Every nonidentity unit-diagonal SPD matrix with
    minimum eigenvalue ``sigma`` has such a representation.
    """
    if not (0.0 < sigma < 1.0):
        raise ValueError("sigma must lie in (0, 1)")
    raw = _matrix(direction)
    h = (raw + raw.T) / 2.0
    h = h - np.diag(np.diag(h))
    minimum = float(np.linalg.eigvalsh(h)[0])
    if minimum >= -1e-14:
        raise ValueError("a nonzero zero-diagonal direction is required")
    alpha = (1.0 - sigma) / (-minimum)
    result = np.eye(h.shape[0]) + alpha * h
    return (result + result.T) / 2.0


def two_step_projection_matrices(a: ArrayLike) -> tuple[FloatMatrix, FloatMatrix, FloatMatrix]:
    """Return with-replacement, without-replacement, and their PSD difference.

    The matrices act in A-energy coordinates, where coordinate updates are
    orthogonal projections Z_i=I-v_i v_i^T.
    """
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    if n < 2:
        raise ValueError("two-step comparison requires n >= 2")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    projections = []
    for index in range(n):
        vector = square_root[:, index]
        projections.append(np.eye(n) - np.outer(vector, vector))
    with_replacement = np.zeros_like(matrix)
    without_replacement = np.zeros_like(matrix)
    for first in range(n):
        for second in range(n):
            term = projections[first] @ projections[second] @ projections[first]
            with_replacement += term
            if first != second:
                without_replacement += term
    with_replacement /= n * n
    without_replacement /= n * (n - 1)
    return with_replacement, without_replacement, with_replacement - without_replacement


def projection_epoch_product(a: ArrayLike, order: Sequence[int]) -> FloatMatrix:
    """Return the epoch product of energy-coordinate hyperplane projections."""
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    if tuple(sorted(order)) != tuple(range(n)):
        raise ValueError("order must be a permutation of range(n)")
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    transform = np.eye(n)
    for index in order:
        vector = square_root[:, index]
        projection = np.eye(n) - np.outer(vector, vector)
        transform = projection @ transform
    return transform


def gram_determinant_rate_bound(a: ArrayLike) -> float:
    r"""Return the Meany/Gram upper bound ``1-det(A)`` for an RPCD epoch.

    The analytic statement is ``rho(E[T\otimes T]) <= 1-det(A)``.  This
    function only evaluates its scalar right-hand side in float64.
    """
    matrix = validate_unit_diagonal_spd(a)
    return float(1.0 - np.linalg.det(matrix))


def spectral_floor_determinant_rate_bound(n: int, sigma: float) -> float:
    r"""Return ``1-sigma^(n-1) (n-(n-1)sigma)``.

    This is the uniform consequence of the Gram-determinant bound when a
    unit-diagonal SPD matrix has minimum eigenvalue ``sigma``.
    """
    if n < 2:
        raise ValueError("dimension must be at least two")
    if not (0.0 < sigma <= 1.0):
        raise ValueError("sigma must lie in (0, 1]")
    determinant_floor = sigma ** (n - 1) * (n - (n - 1) * sigma)
    return float(1.0 - determinant_floor)


def structured_hessian(n: int, sigma: float, signs: Sequence[float] | None = None) -> FloatMatrix:
    """Return sigma I + (1-sigma) ss^T with unit-modulus sign vector s."""
    if n < 2:
        raise ValueError("structured test family requires n >= 2")
    if not (0.0 < sigma <= 1.0):
        raise ValueError("sigma must lie in (0, 1]")
    sign_vector = np.ones(n) if signs is None else np.asarray(signs, dtype=np.float64)
    if sign_vector.shape != (n,) or not np.allclose(np.abs(sign_vector), 1.0):
        raise ValueError("signs must be a length-n vector with entries +/-1")
    return sigma * np.eye(n) + (1.0 - sigma) * np.outer(sign_vector, sign_vector)


def random_correlation(n: int, seed: int, ridge: float = 0.1) -> FloatMatrix:
    if n < 2:
        raise ValueError("n must be at least 2")
    if ridge <= 0.0:
        raise ValueError("ridge must be positive")
    generator = np.random.default_rng(seed)
    x = generator.normal(size=(n, n))
    gram = x.T @ x + ridge * np.eye(n)
    return normalize_unit_diagonal(gram)


def set_minimum_eigenvalue(a: ArrayLike, sigma: float) -> FloatMatrix:
    """Affine-mix a correlation matrix with I so its minimum eigenvalue is sigma."""
    matrix = validate_unit_diagonal_spd(a)
    if not (0.0 < sigma <= 1.0):
        raise ValueError("sigma must lie in (0, 1]")
    minimum = float(np.linalg.eigvalsh(matrix)[0])
    if abs(1.0 - minimum) < 1e-14:
        return np.eye(matrix.shape[0])
    alpha = (1.0 - sigma) / (1.0 - minimum)
    result = alpha * matrix + (1.0 - alpha) * np.eye(matrix.shape[0])
    return (result + result.T) / 2.0


def identity_errors(a: ArrayLike, max_dimension: int = 8) -> dict[str, float]:
    """Return exhaustive residuals for the algebra used by candidate C010."""
    matrix = validate_unit_diagonal_spd(a)
    n = matrix.shape[0]
    product_factor_error = 0.0
    energy_identity_error = 0.0
    for order in all_orders(n, max_dimension=max_dimension):
        product_transform = epoch_operator_product(matrix, order)
        factor_transform = epoch_operator_factor(matrix, order)
        product_factor_error = max(
            product_factor_error,
            float(np.max(np.abs(product_transform - factor_transform))),
        )
        factor = permutation_factor(matrix, order)
        left = matrix - factor_transform.T @ matrix @ factor_transform
        right = matrix @ np.linalg.inv(factor @ factor.T) @ matrix
        energy_identity_error = max(
            energy_identity_error,
            float(np.max(np.abs(left - right))),
        )

    expected_gram_error = float(
        np.max(
            np.abs(
                expected_factor_gram(matrix, max_dimension=max_dimension)
                - (matrix + matrix_jensen_s(matrix))
            )
        )
    )
    jensen_residual = matrix_jensen_upper_matrix(matrix) - expected_energy_pushforward(
        matrix, max_dimension=max_dimension
    )
    jensen_min_eigenvalue = float(
        np.linalg.eigvalsh((jensen_residual + jensen_residual.T) / 2.0)[0]
    )
    return {
        "product_factor_max_abs": product_factor_error,
        "energy_identity_max_abs": energy_identity_error,
        "expected_factor_gram_max_abs": expected_gram_error,
        "jensen_residual_min_eigenvalue": jensen_min_eigenvalue,
    }


def matrix_record(a: ArrayLike, max_dimension: int = 8) -> dict[str, object]:
    matrix = validate_unit_diagonal_spd(a)
    diagnostics = matrix_diagnostics(matrix)
    rate = exact_rpcd_rate(matrix, max_dimension=max_dimension)
    conjectured = conjectured_rate_bound(matrix.shape[0], diagnostics.min_eigenvalue)
    jensen = matrix_jensen_rate(matrix)
    return {
        "matrix": matrix.tolist(),
        "dimension": diagnostics.dimension,
        "eigenvalues": np.linalg.eigvalsh(matrix).tolist(),
        "rpcd_second_moment_rate": rate,
        "conjectured_bound": conjectured,
        "conjecture_margin": conjectured - rate,
        "matrix_jensen_bound": jensen,
        "matrix_jensen_margin": jensen - rate,
        "jensen_to_conjecture_margin": conjectured - jensen,
        "identity_errors": identity_errors(matrix, max_dimension=max_dimension),
    }
