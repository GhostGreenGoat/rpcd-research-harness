"""Exact rank-one counterexample to the remaining-frame inverse inequality."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    m = 6
    identity = sp.eye(m)
    ones = sp.ones(m)
    gram = (identity + ones) / 2
    resolvent = (identity + gram).inv()
    gap = sp.diag(*resolvent.diagonal()) - (identity - resolvent) ** 2
    parallel = sp.ones(m, 1)
    parallel_coefficient = sp.factor(
        (parallel.T * gap * parallel)[0] / (parallel.T * parallel)[0]
    )
    records = {
        "m": m,
        "gram": [[str(gram[i, j]) for j in range(m)] for i in range(m)],
        "gram_eigenvalues": [str(x) for x in gram.eigenvals().keys()],
        "resolvent_parallel_eigenvalue": "2/9",
        "resolvent_transverse_eigenvalue": "2/3",
        "resolvent_diagonal": str(resolvent[0, 0]),
        "parallel_gap": str(parallel_coefficient),
        "expected_parallel_gap": "-1/81",
        "checks": {
            "gram_spd": bool(all(x > 0 for x in gram.eigenvals())),
            "gap_is_negative": bool(parallel_coefficient < 0),
            "exact_value": bool(parallel_coefficient == -sp.Rational(1, 81)),
        },
        "scope": (
            "Refutes the universal orthogonal-projection Bellman inequality; "
            "does not by itself refute its restriction to RPCD covariance-lift projections."
        ),
    }
    path = Path(
        "research/iteration6/root/evidence/REMAINING_FRAME_INVERSE_EXACT_COUNTEREXAMPLE.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
