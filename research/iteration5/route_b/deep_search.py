"""Second-stage structured optimizers for Iteration 5 Route B.

All outputs are E1 float64 evidence.  This file deliberately searches families
that the Iteration-4 generic low-rank optimizer did not parameterize directly:
heterogeneous one-factor blocks, local multiscale perturbations, and dimension
scaling of a fixed group geometry.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import evaluate_family


def logit(value: np.ndarray | float) -> np.ndarray | float:
    value = np.clip(value, 1e-8, 1.0 - 1e-8)
    return np.log(value / (1.0 - value))


def logistic(value: np.ndarray | float) -> np.ndarray | float:
    value = np.clip(value, -18.0, 18.0)
    return 1.0 / (1.0 + np.exp(-value))


def heterogeneous_one_factor(seed: int, evaluations: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    count_families = [
        (4, 5, 6, 7, 8),
        (2, 4, 7, 8, 9),
        (3, 3, 5, 8, 11),
        (2, 3, 4, 6, 7, 8),
    ]
    best = None
    sector_counts: dict[str, int] = {}
    started = time.time()
    for evaluation in range(evaluations):
        counts = count_families[evaluation % len(count_families)]
        groups = len(counts)
        directions = np.ones((groups, 1))
        # Endpoint-heavy loadings directly test simultaneous rank-one and
        # simplex-like transverse scales inside different blocks.
        masses = np.clip(rng.beta(0.45, 0.45, size=groups), 5e-4, 0.9995)
        selector = rng.random()
        if selector < 0.60:
            mu = 1.0 - 10.0 ** rng.uniform(-4.5, -0.15)
        else:
            mu = 10.0 ** rng.uniform(-5.0, -0.05)
        item = evaluate_family(
            "heterogeneous_one_factor",
            counts,
            directions,
            masses,
            mu,
            {"evaluation": evaluation},
        )
        sector = item["result"]["sector"]
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        if best is None or item["ratio"] < best["ratio"]:
            best = item
    return {
        "evidence_level": "E1 float64 search; null result is not proof",
        "avenue": "five/six heterogeneous exchangeable blocks sharing one latent factor",
        "seed": seed,
        "evaluations": evaluations,
        "count_families": [list(x) for x in count_families],
        "sector_counts": sector_counts,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def local_multiscale_refine(
    seed: int, evaluations: int, initial_path: Path, counts: tuple[int, ...]
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    initial_document = json.loads(initial_path.read_text(encoding="utf-8"))
    initial = initial_document.get("global_best", initial_document.get("best", initial_document))
    if len(counts) != len(initial["directions"]):
        raise ValueError("the count vector must match the candidate group count")
    directions = np.asarray(initial["directions"], dtype=float)
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    mass_logits = np.asarray(logit(np.asarray(initial["mass_fractions"])), dtype=float)
    mu_logit = float(logit(float(initial["mu_parameter"])))

    current = evaluate_family(
        "local_multiscale_refine", counts, directions, logistic(mass_logits), float(logistic(mu_logit))
    )
    best = current
    accepted = 0
    history = [{"evaluation": 0, "ratio": best["ratio"]}]
    started = time.time()
    for evaluation in range(1, evaluations + 1):
        fraction = evaluation / evaluations
        direction_scale = 0.16 * (1.0 - fraction) + 0.008
        scalar_scale = 0.55 * (1.0 - fraction) + 0.025
        proposal_directions = directions + direction_scale * rng.normal(size=directions.shape)
        proposal_directions /= np.linalg.norm(proposal_directions, axis=1)[:, None]
        proposal_masses = mass_logits + scalar_scale * rng.normal(size=mass_logits.shape)
        proposal_mu = mu_logit + scalar_scale * float(rng.normal())
        item = evaluate_family(
            "local_multiscale_refine",
            counts,
            proposal_directions,
            logistic(proposal_masses),
            float(logistic(proposal_mu)),
            {"evaluation": evaluation},
        )
        temperature = 0.01 * (1.0 - fraction)
        accept = item["ratio"] < current["ratio"]
        if not accept and temperature > 0:
            accept = rng.random() < math.exp(-(item["ratio"] - current["ratio"]) / temperature)
        if accept:
            directions = proposal_directions
            mass_logits = proposal_masses
            mu_logit = proposal_mu
            current = item
            accepted += 1
        if item["ratio"] < best["ratio"]:
            best = item
            history.append({"evaluation": evaluation, "ratio": best["ratio"]})
    return {
        "evidence_level": "E1 float64 local stochastic refinement; null result is not proof",
        "avenue": f"local refinement of a four-group candidate at n={sum(counts)}",
        "seed": seed,
        "evaluations": evaluations,
        "accepted": accepted,
        "initial_source": str(initial_path),
        "history": history,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def scaling_study(candidate: dict[str, object]) -> dict[str, object]:
    directions = np.asarray(candidate["directions"], dtype=float)
    masses = candidate["mass_fractions"]
    mu = candidate["mu_parameter"]
    count_sequence = [
        (4, 7, 11, 17),
        (6, 10, 16, 26),
        (8, 13, 21, 34),
        (10, 16, 26, 43),
        (12, 20, 32, 52),
    ]
    values = []
    started = time.time()
    for counts in count_sequence:
        item = evaluate_family("dimension_scaling", counts, directions, masses, mu)
        values.append(
            {
                "counts": list(counts),
                "n": sum(counts),
                "ratio": item["ratio"],
                "margin_over_half": item["margin_over_half"],
                "sector": item["result"]["sector"],
                "states_evaluated": item["result"]["states_evaluated"],
                "leaf_underflows": item["result"]["leaf_underflows"],
            }
        )
    return {
        "evidence_level": "E1 float64 dimension-scaling diagnostic; no extrapolation is a proof",
        "fixed_geometry_source": candidate,
        "values": values,
        "elapsed_seconds": time.time() - started,
    }


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("one_factor", "refine", "scale"))
    parser.add_argument("--seed", type=int, default=202608216)
    parser.add_argument("--evaluations", type=int, default=120)
    parser.add_argument(
        "--counts",
        type=str,
        default="6,10,16,26",
        help="comma-separated group counts for refine mode",
    )
    parser.add_argument(
        "--initial",
        type=Path,
        default=Path(__file__).with_name("search_initial.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "one_factor":
        result = heterogeneous_one_factor(args.seed, args.evaluations)
    elif args.mode == "refine":
        counts = tuple(int(value) for value in args.counts.split(","))
        result = local_multiscale_refine(args.seed, args.evaluations, args.initial, counts)
    else:
        document = json.loads(args.initial.read_text(encoding="utf-8"))
        candidate = document.get("best", document.get("global_best", document))
        result = scaling_study(candidate)
    write(args.output, result)
    best = result.get("best", result.get("values"))
    print(json.dumps({"output": str(args.output), "summary": best}, indent=2))


if __name__ == "__main__":
    main()
