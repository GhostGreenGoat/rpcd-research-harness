"""Symbolic two-projection case of the remaining-frame inverse candidate."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    t = sp.symbols("t", nonnegative=True)
    c = (1 - t**2) / (1 + t**2)
    s = 2 * t / (1 + t**2)
    q1 = sp.Matrix([[1, 0], [0, 0]])
    u = sp.Matrix([c, s])
    q2 = u * u.T
    identity = sp.eye(2)
    p1, p2 = identity - q1, identity - q2
    frame = q1 + q2
    rhs = (identity + frame).inv()
    lhs = (
        p1 * (identity + q2).inv() * p1
        + p2 * (identity + q1).inv() * p2
    ) / 2
    gap = sp.simplify(rhs - lhs)
    phi = sp.simplify(frame * (identity + frame).inv())
    parallel = sp.simplify(p1 - p1 * (frame + p1).inv() * p1)
    anticommutator_gap = sp.simplify(parallel - (p1 * phi + phi * p1) / 2)
    records = {
        "gap_entries": [[str(sp.factor(gap[i, j])) for j in range(2)] for i in range(2)],
        "leading_principal_minor": str(sp.factor(gap[0, 0])),
        "determinant": str(sp.factor(gap.det())),
        "trace": str(sp.factor(sp.trace(gap))),
        "parallel_anticommutator_gap_entries": [
            [str(sp.factor(anticommutator_gap[i, j])) for j in range(2)]
            for i in range(2)
        ],
        "parallel_anticommutator_gap_determinant": str(
            sp.factor(anticommutator_gap.det())
        ),
        "scope": "Rational angle parametrization; t>=0 covers all unoriented principal angles.",
    }
    path = Path("research/iteration6/root/evidence/REMAINING_FRAME_INVERSE_M2_SYMBOLIC.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
