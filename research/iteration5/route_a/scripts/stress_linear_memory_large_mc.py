"""Larger-dimensional Monte Carlo hostile control for the half-memory state."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def local_inverse(matrix_m: np.ndarray, q: int) -> np.ndarray:
    n = len(matrix_m)
    matrix_d = np.zeros_like(matrix_m)
    for k in range(n):
        start = max(0, k - q)
        matrix_d[k, k] = 1.0
        # Solve d M=e_k^T backwards without repeatedly inverting blocks.
        for j in range(k - 1, start - 1, -1):
            matrix_d[k, j] = -float(
                matrix_d[k, j + 1 : k + 1] @ matrix_m[j + 1 : k + 1, j]
            )
    return matrix_d


def sampled_certificate(
    matrix_b: np.ndarray, q: int, orders: list[np.ndarray]
) -> tuple[float, float]:
    n = len(matrix_b)
    matrix_p = np.zeros_like(matrix_b)
    matrix_q = np.zeros_like(matrix_b)
    for order in orders:
        ordered_b = matrix_b[np.ix_(order, order)]
        matrix_m = np.tril(ordered_b, -1) + np.eye(n)
        matrix_d = local_inverse(matrix_m, q)
        matrix_r = matrix_d.T @ matrix_d
        ordered_q = matrix_r @ matrix_m @ matrix_m.T @ matrix_r
        inverse_order = np.argsort(order)
        matrix_p += matrix_r[np.ix_(inverse_order, inverse_order)]
        matrix_q += ordered_q[np.ix_(inverse_order, inverse_order)]
    matrix_p /= len(orders)
    matrix_q /= len(orders)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix_b)
    mu = float(eigenvalues[0])
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    certificate = (
        square_root @ matrix_p @ np.linalg.solve(matrix_q, matrix_p) @ square_root / mu
    )
    certificate = (certificate + certificate.T) / 2
    return float(np.linalg.eigvalsh(certificate)[0]), float(np.linalg.cond(matrix_q))


def normalize(matrix: np.ndarray) -> np.ndarray:
    diagonal = np.sqrt(np.diag(matrix))
    return matrix / diagonal[:, None] / diagonal[None, :]


def matrices(n: int, rng: np.random.Generator):
    for rank in [2, 3, max(2, n // 3)]:
        vectors = rng.normal(size=(n, rank))
        gram = normalize(vectors @ vectors.T)
        for epsilon in [0.01, 0.1, 0.5, 0.9]:
            yield f"rank_{rank}_lift_{epsilon}", epsilon * np.eye(n) + (1 - epsilon) * gram
    for c in [1.0, 4.0, 10.0]:
        rho = min(c / n, 0.9)
        yield f"positive_equicorr_c_{c}", (1 - rho) * np.eye(n) + rho * np.ones((n, n))
    for fraction in [0.5, 0.95]:
        rho = -fraction / (n - 1)
        yield f"negative_equicorr_{fraction}", (1 - rho) * np.eye(n) + rho * np.ones((n, n))


def main() -> None:
    seed = 529106
    samples_per_batch = 600
    rng = np.random.default_rng(seed)
    records = []
    worst = None
    for n in [10, 16, 24]:
        q = (n + 1) // 2
        order_batches = [
            [rng.permutation(n) for _ in range(samples_per_batch)] for _ in range(2)
        ]
        for label, matrix_b in matrices(n, rng):
            values = [sampled_certificate(matrix_b, q, batch)[0] for batch in order_batches]
            condition = sampled_certificate(matrix_b, q, order_batches[0])[1]
            entry = {
                "n": n,
                "q": q,
                "label": label,
                "batch_certificates": values,
                "batch_disagreement": abs(values[0] - values[1]),
                "condition_q_first_batch": condition,
            }
            records.append(entry)
            candidate = min(values)
            if worst is None or candidate < worst[0]:
                worst = (candidate, entry)

    assert worst is not None
    output = {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 Monte Carlo hostile control",
        "seed": seed,
        "samples_per_independent_batch": samples_per_batch,
        "records": records,
        "worst_sampled_certificate": worst[0],
        "worst_record": worst[1],
        "result": (
            "no sampled violation"
            if worst[0] >= 0.5
            else "possible violation; increase samples and reconstruct exactly"
        ),
        "limitations": (
            "Permutation expectations are Monte Carlo estimates. Batch "
            "disagreement is a stability diagnostic, not a certified error bar."
        ),
    }
    path = Path(
        "research/iteration5/route_a/evidence/linear_memory_large_mc.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {"output": str(path), "result": output["result"], "worst": worst[0]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
