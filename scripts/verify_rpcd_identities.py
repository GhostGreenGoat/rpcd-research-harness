#!/usr/bin/env python3
"""Reviewer-facing finite checks for the RPCD formulas.

Every permutation is enumerated for each listed matrix.  The combinatorial
average is exact, while matrix inversion and eigendecomposition use float64 and
must therefore be described as numerical verification, not a general proof.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpcd_harness.rpcd import (
    matrix_record,
    random_correlation,
    set_minimum_eigenvalue,
    structured_hessian,
)


TOLERANCE = 2e-10


def verifier_cases() -> list[tuple[str, np.ndarray]]:
    rational_barrier = np.array(
        [
            [1.0, -0.754, 0.816, -0.783],
            [-0.754, 1.0, -0.858, 0.771],
            [0.816, -0.858, 1.0, -0.696],
            [-0.783, 0.771, -0.696, 1.0],
        ]
    )
    return [
        ("identity-n3", np.eye(3)),
        ("structured-n2-s020", structured_hessian(2, 0.20)),
        ("structured-n3-s040-signed", structured_hessian(3, 0.40, [1, -1, 1])),
        ("structured-n4-s070", structured_hessian(4, 0.70)),
        ("random-n3-seed11-s025", set_minimum_eigenvalue(random_correlation(3, 11), 0.25)),
        ("random-n4-seed23-s055", set_minimum_eigenvalue(random_correlation(4, 23), 0.55)),
        (
            "rational-jensen-route-barrier-n4",
            rational_barrier,
        ),
    ]


def build_certificate() -> dict[str, object]:
    records = []
    for label, matrix in verifier_cases():
        record = matrix_record(matrix)
        record["label"] = label
        errors = record["identity_errors"]
        assert errors["product_factor_max_abs"] < TOLERANCE, (label, errors)
        assert errors["energy_identity_max_abs"] < TOLERANCE, (label, errors)
        assert errors["expected_factor_gram_max_abs"] < TOLERANCE, (label, errors)
        assert errors["jensen_residual_min_eigenvalue"] > -TOLERANCE, (label, errors)
        assert record["conjecture_margin"] > -TOLERANCE, (label, record["conjecture_margin"])
        assert record["matrix_jensen_margin"] > -TOLERANCE, (
            label,
            record["matrix_jensen_margin"],
        )
        if label == "rational-jensen-route-barrier-n4":
            assert record["jensen_to_conjecture_margin"] < -0.03, record
        records.append(record)
    return {
        "schema_version": "1.0",
        "kind": "finite-floating-point-certificate",
        "evidence_ceiling": "E2",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "tolerance": TOLERANCE,
        "enumeration": "all n! permutations for every matrix",
        "warning": "Exhaustive permutations plus float64 linear algebra is not a proof for arbitrary n.",
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
