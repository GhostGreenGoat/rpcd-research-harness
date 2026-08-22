"""Auditable effective-width snapshots for the RPCD route portfolio.

The score is deliberately supplied by a reviewer rather than inferred from
text embeddings.  A snapshot must expose every weight, every pairwise route
similarity, and a rationale, so ``B_eff`` remains a reproducible portfolio
diagnostic instead of a hidden mathematical-confidence score.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .routes import active_frontier_routes


SNAPSHOT_KINDS = {"planning_estimate", "post_rollout_review"}


class BreadthError(ValueError):
    """Raised when an effective-breadth snapshot is incomplete or invalid."""


def _pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left <= right else (right, left)


def validate_breadth_snapshot(
    snapshot: Mapping[str, Any],
    *,
    routes: Sequence[Mapping[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "snapshot_id",
        "kind",
        "reviewer",
        "created_at",
        "entries",
        "similarities",
        "limitations",
    }
    missing = sorted(required - set(snapshot))
    extra = sorted(set(snapshot) - required)
    if missing:
        errors.append(f"breadth snapshot missing fields: {missing}")
    if extra:
        errors.append(f"breadth snapshot has unsupported fields: {extra}")
    if snapshot.get("schema_version") != "1.0":
        errors.append("unsupported breadth snapshot schema version")
    if snapshot.get("kind") not in SNAPSHOT_KINDS:
        errors.append("breadth snapshot kind is invalid")
    for field in ("snapshot_id", "reviewer", "created_at"):
        if not isinstance(snapshot.get(field), str) or not snapshot[field].strip():
            errors.append(f"breadth snapshot {field} must be a non-empty string")
    limitations = snapshot.get("limitations")
    if not isinstance(limitations, list) or not limitations or not all(
        isinstance(item, str) and item.strip() for item in limitations
    ):
        errors.append("breadth snapshot limitations must be a non-empty string array")

    entries = snapshot.get("entries")
    route_ids: list[str] = []
    weights: dict[str, float] = {}
    if not isinstance(entries, list) or not entries:
        errors.append("breadth snapshot entries must be a non-empty array")
    else:
        for index, entry in enumerate(entries):
            if not isinstance(entry, Mapping):
                errors.append(f"entries[{index}] must be an object")
                continue
            if set(entry) != {"route_id", "weight"}:
                errors.append(f"entries[{index}] must contain only route_id and weight")
            route_id = entry.get("route_id")
            weight = entry.get("weight")
            if not isinstance(route_id, str) or not route_id.strip():
                errors.append(f"entries[{index}].route_id must be non-empty")
                continue
            if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight < 0:
                errors.append(f"entries[{index}].weight must be non-negative")
                continue
            route_ids.append(route_id)
            weights[route_id] = float(weight)
        if len(route_ids) != len(set(route_ids)):
            errors.append("breadth snapshot route_ids must be unique")
        if weights and sum(weights.values()) <= 0:
            errors.append("breadth snapshot must assign positive total weight")

    if routes is not None and route_ids:
        frontier_ids = {
            str(route.get("route_id")) for route in active_frontier_routes(routes)
        }
        unknown = sorted(set(route_ids) - frontier_ids)
        if unknown:
            errors.append(
                "breadth snapshot includes routes outside the active frontier: " + ", ".join(unknown)
            )
        missing_frontier = sorted(frontier_ids - set(route_ids))
        if missing_frontier:
            errors.append(
                "breadth snapshot omits active frontier routes: "
                + ", ".join(missing_frontier)
            )

    similarities = snapshot.get("similarities")
    seen_pairs: set[tuple[str, str]] = set()
    values: dict[tuple[str, str], float] = {}
    if not isinstance(similarities, list):
        errors.append("breadth snapshot similarities must be an array")
    else:
        for index, entry in enumerate(similarities):
            if not isinstance(entry, Mapping):
                errors.append(f"similarities[{index}] must be an object")
                continue
            if set(entry) != {"route_a", "route_b", "value", "rationale"}:
                errors.append(
                    f"similarities[{index}] must contain route_a, route_b, value, rationale"
                )
            left = entry.get("route_a")
            right = entry.get("route_b")
            value = entry.get("value")
            rationale = entry.get("rationale")
            if left not in weights or right not in weights:
                errors.append(f"similarities[{index}] references an unlisted route")
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
                errors.append(f"similarities[{index}].value must lie in [0, 1]")
                continue
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append(f"similarities[{index}].rationale must be non-empty")
            pair = _pair(str(left), str(right))
            if pair in seen_pairs:
                errors.append(f"duplicate similarity pair: {pair[0]}, {pair[1]}")
            seen_pairs.add(pair)
            values[pair] = float(value)
            if left == right and abs(float(value) - 1.0) > 1e-12:
                errors.append(f"diagonal similarity for {left} must equal one")

    expected_pairs = {
        _pair(left, right)
        for index, left in enumerate(route_ids)
        for right in route_ids[index:]
    }
    missing_pairs = sorted(expected_pairs - seen_pairs)
    if missing_pairs:
        errors.append(
            "breadth snapshot is missing similarity pairs: "
            + ", ".join(f"{left}/{right}" for left, right in missing_pairs)
        )
    return errors


def compute_effective_breadth(
    snapshot: Mapping[str, Any],
    *,
    routes: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    errors = validate_breadth_snapshot(snapshot, routes=routes)
    if errors:
        raise BreadthError("invalid breadth snapshot: " + "; ".join(errors))
    weights = {
        entry["route_id"]: float(entry["weight"]) for entry in snapshot["entries"]
    }
    similarities = {
        _pair(entry["route_a"], entry["route_b"]): float(entry["value"])
        for entry in snapshot["similarities"]
    }
    numerator = sum(weights.values()) ** 2
    denominator = sum(
        left_weight * right_weight * similarities[_pair(left, right)]
        for left, left_weight in weights.items()
        for right, right_weight in weights.items()
    )
    if denominator <= 0:
        raise BreadthError("breadth denominator must be positive")
    return {
        "schema_version": "1.0",
        "snapshot_id": snapshot["snapshot_id"],
        "kind": snapshot["kind"],
        "route_count": len(weights),
        "total_weight": sum(weights.values()),
        "quadratic_similarity_mass": denominator,
        "effective_breadth": numerator / denominator,
        "diagnostic_only": True,
    }


def load_breadth_snapshot(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BreadthError(f"cannot read breadth snapshot {path}: {error}") from error
    if not isinstance(value, dict):
        raise BreadthError(f"expected an object in breadth snapshot {path}")
    return value
