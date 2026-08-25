"""Verify the curated Iteration-7 T143 handoff without requiring ignored runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "research" / "iteration7" / "p1_sealed_breadth"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    errors: list[str] = []
    manifest = json.loads((HANDOFF / "portable_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("kind") != "rpcd-curated-portable-handoff":
        errors.append("portable manifest kind is incorrect")
    if manifest.get("full_run_revalidation_available") is not False:
        errors.append("curated handoff must not claim full run revalidation")

    for record in manifest.get("files", []):
        relative = record.get("portable_path")
        if not isinstance(relative, str):
            errors.append("portable manifest record has no path")
            continue
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"portable path escapes repository: {relative}")
            continue
        if not path.is_file():
            errors.append(f"portable file is missing: {relative}")
            continue
        if path.stat().st_size != record.get("portable_bytes"):
            errors.append(f"portable size mismatch: {relative}")
        if sha256_file(path) != record.get("portable_sha256"):
            errors.append(f"portable SHA-256 mismatch: {relative}")

    ensemble = json.loads((HANDOFF / "ensemble.json").read_text(encoding="utf-8"))
    if ensemble.get("complete") is not True or ensemble.get("dry_run") is not False:
        errors.append("reference ensemble is not a complete real fanout")
    rollouts = ensemble.get("rollouts", [])
    if len(rollouts) != 4 or any(item.get("status") != "completed" for item in rollouts):
        errors.append("reference ensemble does not contain four completed rollouts")
    if len({item.get("method_family") for item in rollouts}) != 4:
        errors.append("reference ensemble method families are not distinct")

    for route_id in (
        "R150-covariance-block-powers",
        "R160-exchangeable-coupling",
        "R180-adaptive-lyapunov",
    ):
        route_path = ROOT / "research" / "routes" / f"{route_id}.json"
        if not route_path.is_file():
            errors.append(f"imported route is missing: {route_id}")
            continue
        route = json.loads(route_path.read_text(encoding="utf-8"))
        source_card = route.get("provenance", {}).get("source_card_path")
        expected_hash = route.get("provenance", {}).get("route_card_hash")
        if not isinstance(source_card, str):
            errors.append(f"route source card is missing: {route_id}")
            continue
        card_path = ROOT / source_card
        if not card_path.is_file() or sha256_file(card_path) != expected_hash:
            errors.append(f"route-card provenance mismatch: {route_id}")

    rejection = json.loads((HANDOFF / "import_rejection.json").read_text(encoding="utf-8"))
    if rejection.get("accepted") is not False or rejection.get("portfolio_eligible") is not False:
        errors.append("rejected polynomial route is incorrectly portfolio eligible")
    if rejection.get("import_command_route_id") != "R170-polynomial-moments":
        errors.append("rejected route ID is incorrect")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "checked_portable_files": len(manifest.get("files", [])),
        "checked_imported_routes": 3,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
