"""Exact diagnostics for the convex/extremal-geometry stitching route.

This script uses rational SymPy arithmetic throughout.  It does *not* prove a
general RPCD inequality; it verifies one deliberately nonsymmetric extreme
point of the 3x3 elliptope and quantifies the distinction between compression
to its kernel and full Loewner (shorted-operator) control.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def lower_triangle(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        matrix.rows,
        matrix.cols,
        lambda row, column: matrix[row, column] if row >= column else 0,
    )


def rational_string(value: sp.Expr) -> str:
    value = sp.factor(value)
    return str(value)


def main() -> None:
    correlation = sp.Matrix(
        [
            [1, 0, sp.Rational(3, 5)],
            [0, 1, sp.Rational(4, 5)],
            [sp.Rational(3, 5), sp.Rational(4, 5), 1],
        ]
    )

    # Gram vectors (1,0), (0,1), (3/5,4/5).  In the symmetric-coordinate
    # convention (h11,h12,h22), v^T H v has middle coefficient 2*v1*v2.
    extremality_constraints = sp.Matrix(
        [
            [1, 0, 0],
            [0, 0, 1],
            [sp.Rational(9, 25), sp.Rational(24, 25), sp.Rational(16, 25)],
        ]
    )
    assert extremality_constraints.det() != 0
    assert correlation.det() == 0
    spectral_variable = correlation.charpoly().gen
    assert sp.expand(correlation.charpoly().as_expr()) == sp.expand(
        spectral_variable * (spectral_variable - 1) * (spectral_variable - 2)
    )

    covariance = sp.zeros(3)
    orders = list(itertools.permutations(range(3)))
    for order in orders:
        permutation = sp.eye(3)[:, list(order)]
        permuted = permutation.T * correlation * permutation
        factor = permutation * lower_triangle(permuted) * permutation.T
        inverse = factor.inv()
        covariance += inverse.T * inverse / len(orders)

    expected_covariance = sp.Matrix(
        [
            [sp.Rational(1523, 1250), sp.Rational(8, 25), -sp.Rational(83, 125)],
            [sp.Rational(8, 25), sp.Rational(849, 625), -sp.Rational(106, 125)],
            [-sp.Rational(83, 125), -sp.Rational(106, 125), sp.Rational(3, 2)],
        ]
    )
    assert covariance == expected_covariance

    kernel = sp.Matrix([-3, -4, 5])
    assert correlation * kernel == sp.zeros(3, 1)
    kernel_norm_squared = (kernel.T * kernel)[0]
    compression = sp.cancel((kernel.T * covariance * kernel)[0] / kernel_norm_squared)

    # Largest alpha for K >= alpha P_span(kernel).  The rank-one domination
    # criterion gives alpha=||z||^2/(z^T K^{-1}z), not the compressed Rayleigh
    # quotient z^T Kz/||z||^2.
    shorted = sp.cancel(
        kernel_norm_squared / (kernel.T * covariance.inv() * kernel)[0]
    )
    schur_gap = sp.cancel(compression - shorted)
    assert compression == sp.Rational(3293, 1250)
    assert shorted == sp.Rational(3157, 1202)
    assert schur_gap == sp.Rational(2984, 375625)
    assert schur_gap > 0

    result = {
        "status": "PASS",
        "evidence_level": "E2 exact finite diagnostic; not a general theorem",
        "correlation": [[rational_string(x) for x in row] for row in correlation.tolist()],
        "spectrum": ["0", "1", "2"],
        "extremality_constraint_determinant": rational_string(
            extremality_constraints.det()
        ),
        "kernel_vector": [str(x) for x in kernel],
        "rpcd_covariance": [
            [rational_string(x) for x in row] for row in covariance.tolist()
        ],
        "kernel_compression_coefficient": rational_string(compression),
        "full_shorted_coefficient": rational_string(shorted),
        "compression_minus_shorted": rational_string(schur_gap),
        "orders_enumerated": len(orders),
        "interpretation": (
            "This nonsymmetric rank-two correlation matrix is an extreme elliptope "
            "point.  Its kernel compression strictly exceeds the coefficient in "
            "the full Loewner bound K >= alpha P_ker."
        ),
    }
    output_path = Path(__file__).with_name("EXTREMAL_GEOMETRY_EXACT.json")
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
