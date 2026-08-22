"""Hostile search for the uncompressed and twice-compressed C3 states.

The null result for the uncompressed state is E1 only.  The compressed state
is expected to fail and is accompanied by an exact rational barrier.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def correlation(raw: np.ndarray) -> np.ndarray:
    gram = raw @ raw.T
    scale = np.sqrt(np.diag(gram))
    return gram / scale[:, None] / scale[None, :]


def states(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    m = matrix.shape[0]
    identity = np.eye(m)
    h = matrix - identity
    h2 = h @ h
    h3 = h2 @ h
    d = np.diag(np.diag(h2))
    e = np.diag(np.diag(h3))
    f = h + h2 - d
    s = (m - 3) * h2 - 2 * h3 + h @ d + d @ h + np.diag(np.diag(f @ f))
    r = (m - 2) * h - h2 + d
    s_compressed = r @ r / (m - 1)

    common = (
        4 * (m - 1) * (m - 2) * identity
        - 10 * (m - 2) * h
        + 8 * h2
        + (3 * m - 14) * d
        - 4 * e
    )
    denominator = 2 * m * (m - 1) * (m - 2)
    uncompressed = (common + 2 * s / (m - 2)) / denominator
    compressed = (common + 2 * s_compressed / (m - 2)) / denominator
    return (uncompressed + uncompressed.T) / 2, (compressed + compressed.T) / 2


def normalized_ratio(matrix: np.ndarray, certificate: np.ndarray) -> float:
    values, vectors = np.linalg.eigh(matrix)
    root = (vectors * np.sqrt(np.maximum(values, 0))) @ vectors.T
    return float(np.linalg.eigvalsh(root @ certificate @ root)[0] / values[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=2026082103)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_c/evidence/ADAPTIVE_STATE_HOSTILE_SEARCH.json"
        ),
    )
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)
    records = {}
    evaluations = 0
    for m in range(3, 13):
        best_u = {"margin": float("inf")}
        best_c = {"margin": float("inf")}
        cases = []
        for sample in range(args.samples):
            rank = int(rng.integers(1, m + 3))
            boundary = correlation(rng.normal(size=(m, rank)))
            mu = 10 ** rng.uniform(-7, -0.0001)
            cases.append((f"random_{sample}_rank_{rank}", mu * np.eye(m) + (1 - mu) * boundary))
        for mu in np.geomspace(1e-8, 0.999, 80):
            cases.append((f"rank_one_{mu:.8g}", mu * np.eye(m) + (1 - mu) * np.ones((m, m))))
            simplex = np.full((m, m), -1 / (m - 1))
            np.fill_diagonal(simplex, 1)
            cases.append((f"simplex_{mu:.8g}", mu * np.eye(m) + (1 - mu) * simplex))
        # Direct sums are a hostile control because scalar child lifting failed
        # first on a rank-one/simplex block mixture.
        for split in range(2, m - 1):
            for mu in np.geomspace(1e-7, 0.999, 24):
                blocks = {}
                for width in (split, m - split):
                    rank_one = mu * np.eye(width) + (1 - mu) * np.ones((width, width))
                    simplex = np.full((width, width), -1 / (width - 1))
                    np.fill_diagonal(simplex, 1)
                    simplex = mu * np.eye(width) + (1 - mu) * simplex
                    blocks[width] = {"r": rank_one, "s": simplex}
                for left in ("r", "s"):
                    for right in ("r", "s"):
                        matrix = np.zeros((m, m))
                        matrix[:split, :split] = blocks[split][left]
                        matrix[split:, split:] = blocks[m - split][right]
                        cases.append(
                            (
                                f"block_{split}_{left}{right}_{mu:.8g}",
                                matrix,
                            )
                        )
        for label, matrix in cases:
            uncompressed, compressed = states(matrix)
            for state, best in ((uncompressed, best_u), (compressed, best_c)):
                ratio = normalized_ratio(matrix, state)
                margin = ratio - 2 / m
                if margin < best["margin"]:
                    best.clear()
                    best.update({"margin": margin, "ratio": ratio, "label": label})
            evaluations += 1
        records[str(m)] = {"uncompressed": best_u, "compressed": best_c}
        records[str(m)]["uncompressed"]["weak_3_over_2m_margin"] = (
            records[str(m)]["uncompressed"]["ratio"] - 1.5 / m
        )
        records[str(m)]["compressed"]["weak_3_over_2m_margin"] = (
            records[str(m)]["compressed"]["ratio"] - 1.5 / m
        )
        print(json.dumps({"m": m, **records[str(m)]}), flush=True)

    result = {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 hostile search",
        "scope_warning": "A null search is not a proof; compressed failures are route failures only.",
        "candidate": "adaptive L3 lower state >= (2mu/m)A^-1",
        "seed": args.seed,
        "random_samples_per_dimension": args.samples,
        "structured_families": "rank-one, simplex, and all two-block rank-one/simplex mixtures",
        "evaluations": evaluations,
        "by_dimension": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "evaluations": evaluations}))


if __name__ == "__main__":
    main()
