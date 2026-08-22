"""Build the portable Route-B search and candidate summaries."""

from __future__ import annotations

import json
import platform
from pathlib import Path

import numpy as np


HERE = Path(__file__).parent


def read(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main() -> None:
    initial = read("search_initial.json")
    one_factor = read("one_factor_search.json")
    refine58 = read("local_refine.json")
    refine76a = read("local_refine_n76.json")
    refine76b = read("local_refine_n76_b.json")
    simplex = read("hierarchical_simplex_g3k20.json")
    triangle = read("duplicate_triangle_n90.json")
    triangle_excess = read("duplicate_triangle_excess_n90.json")
    satellite300 = read("two_group_satellite_n300.json")
    satellite1000 = read("two_group_satellite_n1000.json")
    two_scale = read("two_scale_satellite_n1000.json")
    threshold = read("satellite_threshold_scan.json")
    threshold100k = read("satellite_threshold_scan_n100000.json")
    controls = read("controls.json")
    validation = read("candidate_validation.json")
    prefix_tail = read("prefix_tail_satellite_n1000.json")
    scale_regimes = read("satellite_scale_regimes.json")
    scaling_fit = read("satellite_scaling_fit.json")

    threshold_records = threshold["records"] + threshold100k["records"]
    closest = min(
        (record["best_H"] for record in threshold_records),
        key=lambda item: item["H_ratio"],
    )
    evaluations = sum(
        [
            initial["total_evaluations"],
            one_factor["evaluations"],
            refine58["evaluations"],
            refine76a["evaluations"],
            refine76b["evaluations"],
            simplex["evaluations"],
            triangle["evaluations"],
            triangle_excess["evaluations"],
            satellite300["evaluations"],
            satellite1000["evaluations"],
            two_scale["evaluations"],
            len(threshold_records)
            * len(threshold["c_values"])
            * len(threshold["t_values"]),
            scale_regimes["total_evaluations"],
            4 * len(scaling_fit["dimensions"]) * len(scaling_fit["cosine_grid"]),
        ]
    )
    search = {
        "schema_version": "1.0",
        "task": "T097-half-depth-counterexample / Iteration 5 Route B",
        "evidence_level": "E1 float64 null searches plus separately identified E2/E3 exact artifacts",
        "candidate_claim": "H_ceil(n/2)(A) >= (lambda_min(A)/2) A^{-1}",
        "outcome": "No counterexample found. The closest grid point is independently protected on its tight direction by an exact finite prefix formula.",
        "maximum_dimension": 100000,
        "structured_evaluations_counted": evaluations,
        "closest_H": closest,
        "violation_found": False,
        "avenues": [
            {
                "name": "three frustrated exchangeable groups",
                "best_ratio": initial["avenues"][0]["best"]["ratio"],
                "source": "search_initial.json",
            },
            {
                "name": "four-group multiscale/global and local optimization",
                "best_ratio": min(
                    initial["avenues"][1]["best"]["ratio"],
                    refine58["best"]["ratio"],
                    refine76a["best"]["ratio"],
                    refine76b["best"]["ratio"],
                ),
                "source": "search_initial.json; local_refine*.json",
            },
            {
                "name": "duplicate pole plus simplex leaves",
                "best_ratio": initial["avenues"][2]["best"]["ratio"],
                "source": "search_initial.json",
            },
            {
                "name": "five/six heterogeneous one-factor groups",
                "best_ratio": one_factor["best"]["ratio"],
                "source": "one_factor_search.json",
            },
            {
                "name": "replicated regular simplex / duplicate triangle",
                "best_ratio": min(simplex["best"]["ratio"], triangle["best"]["ratio"]),
                "best_excess_over_signed_rank_one": triangle_excess["best"]["excess_over_signed_rank_one"],
                "source": "hierarchical_simplex_g3k20.json; duplicate_triangle*.json",
            },
            {
                "name": "large-n two-coordinate satellite and multiscale satellite",
                "best_ratio_stochastic_n1000": min(
                    satellite1000["best_ratio"]["ratio"], two_scale["best_ratio"]["ratio"]
                ),
                "best_ratio_threshold_grid": closest["H_ratio"],
                "source": "two_group_satellite*.json; two_scale_satellite_n1000.json; satellite_threshold_scan*.json",
            },
            {
                "name": "fixed, sqrt(n), n^(3/4), and linear satellite-count scaling",
                "finite_grid_closest": scale_regimes["global_closest_to_half"],
                "boundary_layer_fits": {
                    name: value["fit"]
                    for name, value in scaling_fit["regimes"].items()
                },
                "source": "satellite_scale_regimes.json; satellite_scaling_fit.json",
            },
        ],
        "hostile_controls": controls,
        "independent_candidate_validation": validation,
        "prefix_vs_tail_n1000": prefix_tail["results"][0],
        "exact_or_proof_draft_artifacts": [
            "pathwise_shortcut_counterexample.json (exact failed-route Fraction certificate)",
            "orthogonal_satellite_exact.json (exact finite rational prefix formulas)",
            "satellite_asymptotic_check.json and satellite_asymptotics.md (fixed-satellite limit)",
            "fixed_k_satellite_exact.json (exact ordered-prefix checks and Bernstein certificates through k=8)",
            "fixed_k_random_z_audit.json (12 exact Fraction controls on general zero-sum vectors)",
            "satellite_scale_regimes.json and satellite_scaling_fit.json (E1 scaling diagnostics)",
        ],
        "seeds": [
            202608215,
            202608216,
            202608217,
            202608218,
            202608220,
            202608221,
            202608222,
            202608223,
            202608224,
            202608225,
        ],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "warning": "A null structured search is not a proof of the universal matrix inequality.",
    }
    (HERE / "search.json").write_text(json.dumps(search, indent=2), encoding="utf-8")

    candidate = {
        "schema_version": "1.0",
        "status": "near_extremal_non_counterexample",
        "evidence_level": "mixed E1 finite float and E3 proof draft on the tight direction",
        "claim_under_attack": "H_ceil(n/2)(A) >= (mu/2) A^{-1}",
        "closest_matrix_family": {
            "n": closest["n"],
            "counts": [closest["n"] - 2, 2],
            "mu": closest["mu"],
            "boundary_gram": "block diagonal J_(n-2) plus J_2 (orthogonal prototype groups)",
            "A_within_off_diagonal": 1.0 - closest["mu"],
            "A_cross_group": 0,
            "spectrum": "mu with multiplicity n-2; n-2-(n-3)mu; 2-mu",
            "depth": (closest["n"] + 1) // 2,
        },
        "float_result": closest,
        "exact_sign_protection": {
            "direction": "difference of the two satellite coordinates",
            "even_n_prefix_ratio": "1/2 + (h-1)((2-mu)^2-1)/(4(2h-1))",
            "odd_n_prefix_ratio": "(h+1)(3+(2-mu)^2)/(4(2h+1))",
            "conclusion": "J_ratio >= 1/2 exactly on this direction, hence H_ratio >= 1/2.",
            "rational_surrogate": "n=1000, mu=49/50: J_ratio=5045399/9990000 > 1/2",
        },
        "fixed_two_satellite_limit": {
            "eta": "(1-mu)(1-t^2)",
            "ratio": "(8-eta^3)/(8(1+mu))",
            "minimum_margin": "(1-mu)(1-(1-mu)^2/4)/(2(1+mu)) > 0",
        },
        "all_fixed_k_transverse_limit": {
            "selection": "S~Binomial(k,1/2), p_j=Pr(S>=j), sum_j p_j=k/2",
            "second_moment": "1/k + [eta^2(kQ_j-W_j^2)+2eta W_j]/[k(k-1)]",
            "sign": "kQ_j>=W_j^2 and w=(2-eta)/(1+mu)>=1, hence R_k>=1/2",
            "scope": "k fixed before N tends to infinity; satellite zero-sum sector only",
            "exact_check": "enumeration equals moment formula and Bernstein certificates are nonnegative for k=2,...,8",
        },
        "counterexample": None,
        "required_next_gate": "A negative candidate elsewhere would require independent high precision and rational/interval reconstruction; no negative candidate was produced here.",
    }
    (HERE / "candidate_certificate.json").write_text(
        json.dumps(candidate, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "search": str(HERE / "search.json"),
                "candidate": str(HERE / "candidate_certificate.json"),
                "evaluations": evaluations,
                "closest": closest,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
