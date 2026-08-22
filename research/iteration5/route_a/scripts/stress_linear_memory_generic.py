"""Float64 hostile scan of the q-step local-inverse dual certificate.

This is explicitly E1 evidence.  It enumerates every order through n=7, but
floating-point margins and finitely many matrices are not a quantified proof.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np


def certificate(matrix_b: np.ndarray, q: int) -> tuple[float, float, float]:
    n = len(matrix_b)
    matrix_p = np.zeros_like(matrix_b)
    matrix_q = np.zeros_like(matrix_b)
    count = 0
    for order_tuple in itertools.permutations(range(n)):
        order = np.asarray(order_tuple)
        ordered_b = matrix_b[np.ix_(order, order)]
        matrix_m = np.tril(ordered_b, -1) + np.eye(n)
        matrix_d = np.zeros_like(matrix_b)
        for k in range(n):
            start = max(0, k - q)
            local_m = matrix_m[start : k + 1, start : k + 1]
            matrix_d[k, start : k + 1] = np.linalg.inv(local_m)[-1]
        matrix_r = matrix_d.T @ matrix_d
        ordered_q = matrix_r @ matrix_m @ matrix_m.T @ matrix_r
        inverse_order = np.argsort(order)
        matrix_p += matrix_r[np.ix_(inverse_order, inverse_order)]
        matrix_q += ordered_q[np.ix_(inverse_order, inverse_order)]
        count += 1
    matrix_p /= count
    matrix_q /= count

    eigenvalues, eigenvectors = np.linalg.eigh(matrix_b)
    mu = float(eigenvalues[0])
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    certificate_matrix = (
        square_root @ matrix_p @ np.linalg.solve(matrix_q, matrix_p) @ square_root / mu
    )
    certificate_matrix = (certificate_matrix + certificate_matrix.T) / 2
    return float(np.linalg.eigvalsh(certificate_matrix)[0]), mu, float(np.linalg.cond(matrix_q))


def normalize_correlation(matrix: np.ndarray) -> np.ndarray:
    diagonal = np.sqrt(np.diag(matrix))
    return matrix / diagonal[:, None] / diagonal[None, :]


def cases(n: int, rng: np.random.Generator):
    for lift_index in range(24):
        rank = int(rng.integers(1, n + 1))
        vectors = rng.normal(size=(n, rank))
        gram = normalize_correlation(vectors @ vectors.T)
        epsilon = 10 ** rng.uniform(-3, -0.01)
        yield f"random_lift_{lift_index}", epsilon * np.eye(n) + (1 - epsilon) * gram

    for mu in [0.01, 0.1, 0.5, 0.9, 0.99]:
        signs = rng.choice([-1.0, 1.0], size=n)
        yield f"signed_rank_one_mu_{mu}", mu * np.eye(n) + (1 - mu) * np.outer(signs, signs)

    for fraction in [0.2, 0.8, 0.99]:
        rho = -fraction / (n - 1)
        yield f"negative_equicorrelation_{fraction}", (1 - rho) * np.eye(n) + rho * np.ones((n, n))

    # Two latent clusters with a small diagonal lift.
    for index in range(8):
        latent = rng.normal(size=(2, 3))
        membership = np.arange(n) % 2
        vectors = latent[membership] + 0.2 * rng.normal(size=(n, 3))
        gram = normalize_correlation(vectors @ vectors.T)
        epsilon = [0.01, 0.1, 0.5, 0.9][index % 4]
        yield f"two_cluster_{index}", epsilon * np.eye(n) + (1 - epsilon) * gram


def main() -> None:
    seed = 529105
    rng = np.random.default_rng(seed)
    records = []
    global_worst = None
    for n in range(3, 8):
        q = min(n - 1, (n + 1) // 2)
        worst = None
        case_count = 0
        for label, matrix_b in cases(n, rng):
            value, mu, condition_q = certificate(matrix_b, q)
            entry = {
                "label": label,
                "minimum_normalized_certificate": value,
                "mu": mu,
                "condition_q": condition_q,
                "matrix": matrix_b.tolist(),
            }
            if worst is None or value < worst["minimum_normalized_certificate"]:
                worst = entry
            if global_worst is None or value < global_worst["minimum_normalized_certificate"]:
                global_worst = {"n": n, "q": q, **entry}
            case_count += 1
        records.append({"n": n, "q": q, "cases": case_count, "worst": worst})

    assert global_worst is not None
    output = {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 exhaustive-order hostile scan",
        "seed": seed,
        "dimensions": records,
        "global_worst": global_worst,
        "target_half_margin": global_worst["minimum_normalized_certificate"] - 0.5,
        "result": (
            "no violation in this finite scan"
            if global_worst["minimum_normalized_certificate"] >= 0.5
            else "candidate violation; exact reconstruction required"
        ),
        "scope": (
            "All permutations are enumerated, but the matrix sample is finite "
            "and arithmetic is float64; this is not theorem evidence."
        ),
    }
    path = Path(
        "research/iteration5/route_a/evidence/linear_memory_generic_stress.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(path),
                "result": output["result"],
                "global_worst": global_worst["minimum_normalized_certificate"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
