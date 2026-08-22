"""Exact finite controls for the half-memory equicorrelation certificate.

The quantified proof is in ``linear_memory_dual.md``.  This verifier loads
the independently written exact block reducer and checks the two Loewner
ingredients and final dual constant on a rational grid.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path


def load_blocks():
    source = Path(
        "research/iteration5/route_a/scripts/linear_memory_equicorrelation.py"
    )
    spec = importlib.util.spec_from_file_location("linear_memory_equicorrelation", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.blocks


def build_record(max_n: int) -> dict[str, object]:
    blocks = load_blocks()
    cases = []
    worst = (F(10), None)
    for n in range(2, max_n + 1):
        q = (n + 1) // 2
        for denominator in (5, 7, 11, 17):
            for numerator in range(1, denominator):
                rho = F(numerator, denominator)
                result = blocks(n, rho, q)
                mu = result["mu"]
                ell = result["ell"]
                p_parallel = result["p_parallel"]
                p_perp = result["p_perp"]
                beta = rho * q * mu**q

                assert ell * p_parallel >= mu / 2
                assert p_perp >= 1
                assert beta < F(2, 5)
                assert result["minimum_normalized"] > F(25, 98)
                if result["minimum_normalized"] < worst[0]:
                    worst = (
                        result["minimum_normalized"],
                        (n, q, rho, result["normalized_perp"], result["normalized_parallel"]),
                    )
        cases.append({"n": n, "q": q, "rational_rhos": 36})

    assert worst[1] is not None
    n, q, rho, transverse, parallel = worst[1]
    return {
        "schema_version": "1.0",
        "status": "E2 exact finite regression for the E3 analytic family proof",
        "claim": "K(B)>=(25mu/98)B^{-1} for positive equicorrelation using q=ceil(n/2) local-inverse dual state",
        "max_n": max_n,
        "cases": cases,
        "worst_exact_grid_case": {
            "n": n,
            "q": q,
            "rho": str(rho),
            "minimum_normalized": str(worst[0]),
            "transverse": str(transverse),
            "parallel": str(parallel),
        },
        "analytic_controls": [
            "ell*p_parallel>=mu/2",
            "p_perp>=1",
            "rho*q*mu^q<=1/e<2/5",
            "Q<(49/25)P",
        ],
        "checks": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER5_LINEAR_MEMORY_FINITE_CERTIFICATE.json"
        ),
    )
    args = parser.parse_args()
    record = build_record(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": record["checks"]}))


if __name__ == "__main__":
    main()
