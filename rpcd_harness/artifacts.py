"""Credential-free zip work packets with SHA-256 manifests."""

from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from .protocol import ProtocolError, load_task, sha256_file


EXCLUDED_TOP_LEVEL = {
    ".git",
    ".codex",
    ".venv",
    "venv",
    "bundles",
    "dist",
    "build",
    "tmp",
}
EXCLUDED_NAMES = {
    "auth.json",
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials",
    "credentials.json",
    "cookies.json",
    "session.json",
    "token.json",
    "secrets.json",
    "client_secret.json",
    "service-account.json",
    ".git-credentials",
    "id_rsa",
    "id_ed25519",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
EXCLUDED_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".pyc", ".pyo"}
EXCLUDED_THIRD_PARTY_DOWNLOADS = {
    Path("research/case_studies/anthropic_zeta_2026/anthropic_zeta_process.pdf"),
    Path("research/case_studies/anthropic_zeta_2026/anthropic_zeta_process_extracted.txt"),
}
SENSITIVE_CONTENT_PATTERNS = {
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"),
    "openai-key": re.compile(rb"sk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "aws-access-key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "slack-token": re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "anthropic-key": re.compile(rb"sk-ant-[A-Za-z0-9_-]{20,}"),
    "google-api-key": re.compile(rb"AIza[0-9A-Za-z_-]{30,}"),
    "stripe-live-key": re.compile(rb"(?:sk|rk)_live_[0-9A-Za-z]{16,}"),
    "huggingface-token": re.compile(rb"hf_[A-Za-z0-9]{20,}"),
    "gitlab-token": re.compile(rb"glpat-[A-Za-z0-9_-]{20,}"),
    "jwt": re.compile(rb"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    "credentialed-url": re.compile(rb"https?://[^\s/:@]+:[^\s/@]+@"),
}
CONTENT_SCAN_CHUNK_BYTES = 1024 * 1024
CONTENT_SCAN_OVERLAP_BYTES = 512


def _is_excluded(relative: Path, include_runs: bool) -> bool:
    if not relative.parts:
        return True
    if relative.parts[0] in EXCLUDED_TOP_LEVEL:
        return True
    if relative.parts[0] == "runs" and not include_runs:
        return True
    if any(part in EXCLUDED_NAMES or part in EXCLUDED_TOP_LEVEL for part in relative.parts):
        return True
    if ".ssh" in relative.parts:
        return True
    if any(part.startswith(".env.") for part in relative.parts):
        return True
    if relative.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if relative in EXCLUDED_THIRD_PARTY_DOWNLOADS:
        return True
    if relative.parts[:2] == ("research", "case_studies") and "parisi_zamponi_jamming_2026" in relative.parts:
        return True
    return False


def _sensitive_content_kind(path: Path) -> str | None:
    try:
        with path.open("rb") as handle:
            overlap = b""
            while True:
                chunk = handle.read(CONTENT_SCAN_CHUNK_BYTES)
                if not chunk:
                    break
                data = overlap + chunk
                for kind, pattern in SENSITIVE_CONTENT_PATTERNS.items():
                    if pattern.search(data):
                        return kind
                overlap = data[-CONTENT_SCAN_OVERLAP_BYTES:]
    except OSError:
        return "unreadable"
    return None


def project_files(
    root: Path, include_runs: bool = False, task_id: str | None = None
) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] == "runs" and include_runs:
            if task_id is None or len(relative.parts) < 2 or relative.parts[1] != task_id:
                continue
        if not _is_excluded(relative, include_runs=include_runs):
            files.append(path)
    return sorted(files)


def create_bundle(root: Path, task_id: str, output: Path, include_runs: bool = False) -> Path:
    task = load_task(root, task_id)
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [
        path
        for path in project_files(root, include_runs=include_runs, task_id=task_id)
        if path.resolve() != output
    ]
    sensitive = [
        (path.relative_to(root).as_posix(), kind)
        for path in files
        if (kind := _sensitive_content_kind(path)) is not None
    ]
    if sensitive:
        details = ", ".join(f"{path} ({kind})" for path, kind in sensitive)
        raise ProtocolError(f"refusing to bundle sensitive content: {details}")
    entries = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in files
    ]
    manifest = {
        "schema_version": "1.0",
        "kind": "rpcd-portable-work-packet",
        "task_id": task["task_id"],
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "include_runs": include_runs,
        "credential_policy": "No credentials or Codex account state are included.",
        "files": entries,
    }
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
        archive.writestr("_bundle/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return output


def _safe_archive_name(name: str) -> bool:
    if not isinstance(name, str) or not name or "\\" in name:
        return False
    path = PurePosixPath(name)
    windows_path = PureWindowsPath(name)
    reserved = {
        "con", "prn", "aux", "nul",
        *(f"com{index}" for index in range(1, 10)),
        *(f"lpt{index}" for index in range(1, 10)),
    }
    unsafe_part = any(
        not part
        or part in {".", ".."}
        or ":" in part
        or part[-1:] in {" ", "."}
        or any(ord(character) < 32 for character in part)
        or part.split(".", 1)[0].casefold() in reserved
        for part in path.parts
    )
    return (
        not path.is_absolute()
        and not windows_path.is_absolute()
        and not windows_path.drive
        and not windows_path.anchor
        and not unsafe_part
    )


def verify_bundle(bundle: Path) -> dict[str, Any]:
    if not bundle.is_file():
        raise ProtocolError(f"bundle does not exist: {bundle}")
    with zipfile.ZipFile(bundle, "r") as archive:
        names = archive.namelist()
        unsafe = [name for name in names if not _safe_archive_name(name)]
        if unsafe:
            raise ProtocolError(f"unsafe archive paths: {unsafe}")
        folded = [name.casefold() for name in names]
        if len(folded) != len(set(folded)):
            raise ProtocolError("archive contains case-insensitive path aliases")
        try:
            manifest = json.loads(archive.read("_bundle/manifest.json"))
        except (KeyError, json.JSONDecodeError) as error:
            raise ProtocolError("bundle has no valid manifest") from error
        declared = {entry["path"]: entry for entry in manifest.get("files", [])}
        actual = {name for name in names if name != "_bundle/manifest.json" and not name.endswith("/")}
        if set(declared) != actual:
            missing = sorted(set(declared) - actual)
            extra = sorted(actual - set(declared))
            raise ProtocolError(f"bundle file set mismatch; missing={missing}, extra={extra}")
        import hashlib

        for name, entry in declared.items():
            data = archive.read(name)
            digest = hashlib.sha256(data).hexdigest()
            if digest != entry["sha256"]:
                raise ProtocolError(f"SHA-256 mismatch for {name}")
            if len(data) != entry["bytes"]:
                raise ProtocolError(f"size mismatch for {name}")
        return manifest


def unpack_bundle(bundle: Path, destination: Path, force: bool = False) -> list[Path]:
    manifest = verify_bundle(bundle)
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with zipfile.ZipFile(bundle, "r") as archive:
        for entry in manifest["files"]:
            name = entry["path"]
            target = (destination / Path(*PurePosixPath(name).parts)).resolve()
            try:
                target.relative_to(destination)
            except ValueError as error:
                raise ProtocolError(f"archive path escapes destination: {name}") from error
            data = archive.read(name)
            if target.exists() and target.read_bytes() != data and not force:
                raise ProtocolError(f"refusing to overwrite different file: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            written.append(target)
    return written
