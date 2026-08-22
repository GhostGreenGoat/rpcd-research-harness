"""Exact barrier to obtaining a positive uniform constant from bare Jensen.

For A = mu I + (1-mu) 11^T, the parallel eigenspaces of A and
S = (A-I)^2/3 + Diag(diag((A-I)^2))/6 coincide.  All arithmetic below is
over Fraction; floating point is used only for the displayed decimal.
"""

from fractions import Fraction


def equicorrelation_parallel(n: int, mu: Fraction) -> dict[str, Fraction]:
    lam = Fraction(n) - (n - 1) * mu
    s = (1 - mu) ** 2 * Fraction((n - 1) * (2 * n - 1), 6)
    jensen_ratio = lam / (mu * (lam + s))
    loewner_margin = (2 - mu) * lam - mu * s
    return {
        "lambda_parallel": lam,
        "S_parallel": s,
        "jensen_gamma_over_mu": jensen_ratio,
        "gap_to_one_half": jensen_ratio - Fraction(1, 2),
        "loewner_margin": loewner_margin,
    }


def main() -> None:
    result = equicorrelation_parallel(21, Fraction(9, 20))
    expected = {
        "lambda_parallel": Fraction(12),
        "S_parallel": Fraction(4961, 120),
        "jensen_gamma_over_mu": Fraction(3200, 6401),
        "gap_to_one_half": Fraction(-1, 12802),
        "loewner_margin": Fraction(-3, 800),
    }
    assert result == expected
    for key, value in result.items():
        print(f"{key}: {value} ({float(value):.16g})")


if __name__ == "__main__":
    main()
