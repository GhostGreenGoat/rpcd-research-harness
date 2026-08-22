"""Symbolic n=2 barriers to naive boundary/identity continuation."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    mu = sp.symbols("mu", real=True)
    q = 1 - mu
    identity = sp.eye(2)
    matrix = sp.Matrix([[1, q], [q, 1]])

    lower = sp.Matrix([[1, 0], [q, 1]])
    upper = lower.T
    inverse_lower = lower.inv()
    inverse_upper = upper.inv()
    covariance = sp.simplify(
        (inverse_lower.T * inverse_lower + inverse_upper.T * inverse_upper) / 2
    )
    expected = sp.Matrix([[1 + q**2 / 2, -q], [-q, 1 + q**2 / 2]])
    assert sp.simplify(covariance - expected) == sp.zeros(2)

    boundary = sp.simplify(covariance.subs(mu, 0))
    chord = sp.simplify((1 - mu) * boundary + mu * identity)
    chord_gap = sp.simplify(covariance - chord)
    assert sp.simplify(chord_gap + mu * (1 - mu) * identity / 2) == sp.zeros(2)

    parallel_change = sp.factor(1 + q**2 / 2 - q - 1)
    transverse_change = sp.factor(1 + q**2 / 2 + q - 1)
    assert sp.factor(parallel_change + q * (2 - q) / 2) == 0
    assert sp.factor(transverse_change - q * (2 + q) / 2) == 0

    result = {
        "status": "PASS",
        "evidence_level": "E2 exact symbolic route barrier",
        "covariance": [[str(sp.factor(x)) for x in row] for row in covariance.tolist()],
        "endpoint_chord_gap": [
            [str(sp.factor(x)) for x in row] for row in chord_gap.tolist()
        ],
        "parallel_change_from_identity": str(parallel_change),
        "transverse_change_from_identity": str(transverse_change),
        "scope": "Refutes interpolation shortcuts only; n=2 RPCD itself is solved.",
    }
    output = Path(__file__).with_name("CONTINUATION_EXACT_BARRIERS.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
