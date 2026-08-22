"""Exact counterexample to a tempting replicated-simplex pathwise proof.

For three duplicate groups at the vertices of a regular simplex and
``mu=1/5``, the second distinguished coordinate in a within-group difference
can have solve magnitude below one.  Thus the signed-rank-one distinguished-
coordinate argument cannot be transferred path by path; averaging is needed.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


def main() -> None:
    groups = 3
    mu = Fraction(1, 5)
    alpha = 1 - mu
    relaxation = alpha * groups / (groups - 1)  # 6/5
    # The first + special in group 0 has already been solved.  The following
    # ordinary pivot groups are then visited before the - special in group 0.
    sequence = (1, 0, 0, 2)
    sums = [Fraction(1), Fraction(0), Fraction(0)]
    trace = []
    for group in sequence:
        mean = sum(sums) / groups
        solved = -relaxation * (sums[group] - mean)
        sums[group] += solved
        trace.append(
            {
                "pivot_group": group,
                "solved": str(solved),
                "group_sums": [str(value) for value in sums],
            }
        )
    mean = sum(sums) / groups
    second_solve = -1 - relaxation * (sums[0] - mean)
    assert second_solve == Fraction(-2889, 3125)
    assert abs(second_solve) < 1
    result = {
        "evidence_level": "E2 exact rational finite failed-route certificate",
        "family": "three duplicate groups at regular-simplex vertices",
        "mu": str(mu),
        "within_off_diagonal_A": str(alpha),
        "cross_group_A": str(-alpha / 2),
        "required_group_sizes": [4, 1, 1],
        "path": ["plus_special_group_0", *[f"ordinary_group_{g}" for g in sequence], "minus_special_group_0"],
        "trace": trace,
        "second_special_solve": str(second_solve),
        "second_special_squared": str(second_solve * second_solve),
        "gap_below_unit_magnitude": str(1 - abs(second_solve)),
        "conclusion": "The pathwise claim that every selected distinguished coordinate contributes squared solve at least one is false for this family. This does not refute the averaged half-depth inequality.",
    }
    output = Path(__file__).with_name("pathwise_shortcut_counterexample.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
