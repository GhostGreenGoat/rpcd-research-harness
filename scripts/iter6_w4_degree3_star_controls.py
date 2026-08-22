"""Three fixed exact controls for the next degree-three-star W4 state."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def l3(matrix: sp.Matrix) -> sp.Matrix:
    d = matrix.rows
    I = sp.eye(d)
    H = matrix - I
    D = sp.diag(*[(H**2)[i, i] for i in range(d)])
    E = sp.diag(*[(H**3)[i, i] for i in range(d)])
    F = H + H**2 - D
    S = (
        (d - 3) * H**2
        - 2 * H**3
        + H * D
        + D * H
        + sp.diag(*[(F**2)[i, i] for i in range(d)])
    )
    return sp.simplify(
        (
            4 * (d - 1) * (d - 2) * I
            - 10 * (d - 2) * H
            + 8 * H**2
            + (3 * d - 14) * D
            - 4 * E
            + 2 * S / (d - 2)
        )
        / (2 * d * (d - 1) * (d - 2))
    )


def check_direction(direction: tuple[sp.Rational, ...]) -> dict[str, object]:
    assert sum(value**2 for value in direction) == 1
    d = 6
    t = Q(99, 100)
    mu = 1 - t
    weights = [t * value for value in direction]
    active_h = sp.zeros(4)
    for index, value in enumerate(weights, start=1):
        active_h[0, index] = value
        active_h[index, 0] = value
    H = sp.diag(active_h, sp.zeros(2))
    C = sp.eye(d) + H
    gap = sp.factor(l3(C) - Q(2, d) * (C + (1 - mu) * sp.eye(d)).inv())
    active = gap[:4, :4]
    minors: list[sp.Expr] = []
    for size in range(1, 5):
        for subset in itertools.combinations(range(4), size):
            value = sp.factor(active.extract(subset, subset).det())
            assert value > 0
            minors.append(value)
    return {
        "direction": [str(value) for value in direction],
        "principal_minor_count": len(minors),
        "minimum_principal_minor": str(min(minors)),
        "determinant": str(sp.factor(active.det())),
    }


def main() -> None:
    directions = [
        (Q(1, 3), Q(2, 3), Q(2, 3)),
        (Q(36, 49), Q(24, 49), Q(23, 49)),
        (Q(12, 13), Q(4, 13), Q(3, 13)),
    ]
    controls = [check_direction(direction) for direction in directions]
    result = {
        "schema_version": "1.0",
        "evidence_level": "E2 fixed exact controls",
        "verdict": "PASS_FOR_LISTED_CONTROLS_ONLY",
        "scope": "d=6, t=99/100, three explicitly listed rational directions",
        "controls": controls,
    }
    output = Path("research/iteration6/route_l3/evidence/W4_DEGREE3_STAR_CONTROLS.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
