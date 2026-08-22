"""Exact fixed-k limiting satellite-prefix polynomials.

For k satellite coordinates with effective equicorrelation eta, the limiting
large-block reduction selects each satellite with probability 1/2 and orders
the selected set uniformly.  This script enumerates those finite ordered
prefixes symbolically for z=e_1-e_2.  The resulting transverse coefficient is
exact over Q[eta].  It is a proof aid for the reduced fixed-k model only.
"""

from __future__ import annotations

import itertools
import json
from math import factorial
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent


def transverse_polynomial(k: int, eta: sp.Symbol) -> sp.Expr:
    """Return E[sum_j y_j^2]/||e1-e2||^2 exactly.

    Each ordered s-tuple has probability 1/(2^k s!).  Along a tuple,
    y_j=z_{i_j}-eta*sum_{l<j} y_l.
    """
    z = (sp.Integer(1), sp.Integer(-1)) + (sp.Integer(0),) * (k - 2)
    total = sp.Integer(0)
    for s in range(1, k + 1):
        subtotal = sp.Integer(0)
        for order in itertools.permutations(range(k), s):
            cumulative = sp.Integer(0)
            energy = sp.Integer(0)
            for index in order:
                solved = z[index] - eta * cumulative
                energy += solved * solved
                cumulative += solved
            subtotal += energy
        total += subtotal / factorial(s)
    return sp.factor(total / (2 ** k * 2))


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
    """Exact coefficients in the degree-d Bernstein basis on [0,1]."""
    poly = sp.Poly(sp.expand(polynomial), variable)
    degree = poly.degree()
    power = [poly.nth(j) for j in range(degree + 1)]
    return [
        sp.factor(sum(
            power[j] * sp.binomial(i, j) / sp.binomial(degree, j)
            for j in range(i + 1)
        ))
        for i in range(degree + 1)
    ]


def second_moment_formula(k: int, eta: sp.Symbol) -> sp.Expr:
    """Closed O(k) formula from exchangeable without-replacement moments."""
    rho = 1 - eta
    result = sp.Integer(0)
    for j in range(1, k + 1):
        tail_probability = sp.Rational(
            sum(sp.binomial(k, s) for s in range(j, k + 1)), 2 ** k
        )
        weights = [rho ** r for r in range(j - 1)]
        weight_sum = sum(weights, sp.Integer(0))
        weight_square_sum = sum((value * value for value in weights), sp.Integer(0))
        normalized_second_moment = (
            sp.Rational(1, k)
            + eta ** 2 * (k * weight_square_sum - weight_sum ** 2) / (k * (k - 1))
            + 2 * eta * weight_sum / (k * (k - 1))
        )
        result += tail_probability * normalized_second_moment
    return sp.factor(result)


def main() -> None:
    eta = sp.symbols("eta", nonnegative=True)
    records = []
    for k in range(2, 9):
        h = transverse_polynomial(k, eta)
        moment_formula = second_moment_formula(k, eta)
        excess = sp.factor(h - sp.Rational(1, 2))
        bernstein = bernstein_coefficients(excess, eta)
        expected_quadratic = (
            sp.Rational(1, 2) + eta / 4 + sp.Rational(k + 1, 24) * eta ** 2
        )
        records.append({
            "k": k,
            "h_k": str(h),
            "second_moment_formula": str(moment_formula),
            "enumeration_minus_second_moment_formula": str(sp.simplify(h - moment_formula)),
            "fixed_k_quadratic_expansion": str(expected_quadratic) + " + O(eta**3)",
            "quadratic_expansion_residual_at_orders_0_1_2": [
                str(sp.expand(h - expected_quadratic).coeff(eta, degree))
                for degree in range(3)
            ],
            "h_k_expanded": str(sp.expand(h)),
            "h_k_minus_half_factored": str(excess),
            "coefficients_h_k_minus_half_low_to_high": [
                str(value) for value in reversed(sp.Poly(excess, eta).all_coeffs())
            ],
            "bernstein_coefficients_on_unit_interval": [
                str(value) for value in bernstein
            ],
            "bernstein_nonnegative_certificate": all(value >= 0 for value in bernstein),
            "h_k_at_eta_half": str(h.subs(eta, sp.Rational(1, 2))),
            "margin_at_eta_half": str(excess.subs(eta, sp.Rational(1, 2))),
        })
    result = {
        "evidence_level": (
            "E2 exact symbolic finite enumeration for the reduced fixed-k limit; "
            "the reduction from finite N remains the E3 proof draft"
        ),
        "definition": (
            "h_k(eta)=2^(-k)/||e1-e2||^2 * sum_s 1/s! * "
            "sum_{distinct ordered i_1...i_s} sum_j y_j^2, "
            "y_j=z_i_j-eta*sum_{l<j}y_l"
        ),
        "full_family_ratio": "R_k(mu,t)=((2-eta)/(1+mu))*h_k(eta), eta=(1-mu)(1-t^2)",
        "all_fixed_k_transverse_argument": {
            "selection_count": "S~Binomial(k,1/2), p_j=Pr(S>=j)",
            "tail_sum": "sum_{j=1}^k p_j=E[S]=k/2",
            "rho": "rho=1-eta in [0,1]",
            "weights": "W_j=sum_{r=0}^{j-2}rho^r, Q_j=sum_{r=0}^{j-2}rho^(2r)",
            "normalized_second_moment": (
                "E[y_j^2 | S>=j]/||z||^2 = 1/k + "
                "eta^2*(k*Q_j-W_j^2)/(k*(k-1)) + "
                "2*eta*W_j/(k*(k-1))"
            ),
            "positivity": (
                "eta,W_j>=0 and k*Q_j>=W_j^2 by Cauchy; summing the "
                "1/k terms against p_j gives 1/2"
            ),
            "scope": (
                "z has zero satellite sum; k is fixed before N tends to infinity; "
                "this proves only the satellite-transverse sector of the limiting family"
            ),
        },
        "ratio_local_expansion": (
            "with alpha=1-mu and u=1-t^2: R_k=1/2+alpha/4+"
            "alpha^2*(1/8+(k-2)*u^2/24)+O_k(alpha^3)"
        ),
        "records": records,
        "all_k_2_through_8_bernstein_certificates_nonnegative": all(
            row["bernstein_nonnegative_certificate"]
            for row in records
        ),
        "warning": (
            "The displayed Bernstein certificates independently prove h_k>=1/2 "
            "for eta in [0,1] and k=2,...,8. The second-moment identity gives "
            "the same sign for every fixed k. Since (2-eta)/(1+mu)>=1 when "
            "eta=(1-mu)(1-t^2), the reduced limiting R_k is also >=1/2. "
            "This does not independently validate the N-to-infinity reduction "
            "or prove the original all-matrix conjecture."
        ),
    }
    output = HERE / "fixed_k_satellite_exact.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
