"""Independent exact reconstruction of the recorded tail-SDP dual witness.

This checker does not import the search generator.  It rebuilds coordinate
updates, epoch products, the four PSD variables, stationarity, normalization,
and the Farkas contradiction from the portable JSON rank-one decomposition.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import sympy as sp


def parse_rational(value: str) -> sp.Rational:
    return sp.Rational(value)


def trace_inner(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.trace(left.T * right)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    arguments = parser.parse_args()
    record = json.loads(arguments.certificate.read_text(encoding="utf-8"))

    matrix = sp.Matrix([[1, sp.Rational(3, 10), 0], [sp.Rational(3, 10), 1, sp.Rational(2, 5)], [0, sp.Rational(2, 5), 1]])
    rate = parse_rational(record["rate"])
    kappa = parse_rational(record["kappa"])
    identity = sp.eye(3)
    updates: list[sp.Matrix] = []
    for index in range(3):
        basis = sp.zeros(3, 1)
        basis[index] = 1
        updates.append(identity - basis * (basis.T * matrix))
    epochs: list[sp.Matrix] = []
    for order in itertools.permutations(range(3)):
        epoch = identity
        for index in order:
            epoch = updates[index] * epoch
        epochs.append(epoch)

    def mstar(weight: sp.Matrix) -> sp.Matrix:
        return sp.simplify(sum((epoch.T * weight * epoch for epoch in epochs), sp.zeros(3)) / 6)

    def mforward(weight: sp.Matrix) -> sp.Matrix:
        return sp.simplify(sum((epoch * weight * epoch.T for epoch in epochs), sp.zeros(3)) / 6)

    variables: dict[str, sp.Matrix] = {}
    positive_coefficients = True
    active_coefficients: list[sp.Rational] = []
    for name in ("L", "U", "X", "Y"):
        reconstructed = sp.zeros(3)
        for term in record["active_rank_one_terms"][name]:
            vector = sp.Matrix(term["ray"])
            coefficient = parse_rational(term["coefficient"])
            active_coefficients.append(coefficient)
            positive_coefficients = positive_coefficients and coefficient > 0
            reconstructed += coefficient * vector * vector.T
        variables[name] = sp.simplify(reconstructed)
        stored = sp.Matrix([[parse_rational(value) for value in row] for row in record["variables"][name]])
        assert variables[name] == stored

    first = mstar(matrix)
    stationarity = sp.simplify(variables["L"] - variables["U"] + rate * variables["X"] + rate * variables["Y"] - mforward(variables["Y"]))
    normalization = sp.factor(trace_inner(variables["U"], matrix))
    gap = sp.factor(trace_inner(variables["X"], first) - kappa * normalization)
    lower_bound = sp.factor(kappa + gap)
    denominator_lcm = sp.ilcm(*(coefficient.q for coefficient in active_coefficients))
    integer_scale = 1000 * denominator_lcm
    integer_gap = sp.factor(integer_scale * gap)
    stored_gap = parse_rational(record["certified_dual_gap_XB_minus_kappa_UA"])

    assert positive_coefficients
    assert stationarity == sp.zeros(3)
    assert normalization == 1
    assert gap == stored_gap
    assert gap > 0
    assert lower_bound == sp.Rational(211356802264686441, 174023970826141000)
    assert denominator_lcm == 522071912478423
    assert all((integer_scale * coefficient).q == 1 for coefficient in active_coefficients)
    assert integer_gap == 7584111819951723

    print(
        json.dumps(
            {
                "status": "PASS",
                "arithmetic": "exact SymPy Rational",
                "tolerance": 0,
                "positive_rank_one_coefficients": True,
                "stored_matrices_reconstructed": True,
                "stationarity_exactly_zero": True,
                "normalization_inner_U_A": str(normalization),
                "positive_dual_gap": str(gap),
                "certified_kappa_tail_lower_bound": str(lower_bound),
                "integer_rank_one_scale": str(integer_scale),
                "integer_scaled_positive_gap": str(integer_gap),
                "conclusion": "The q=3/20, kappa=6/5 two-facet tail SDP is infeasible for the recorded rational n=3 A.",
                "scope": "Finite instance/constant separation only; not a counterexample to C050.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
