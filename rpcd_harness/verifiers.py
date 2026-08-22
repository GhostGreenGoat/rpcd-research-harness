"""Trusted, shell-free execution of task-declared verifier commands.

Verifier specifications are repository-owned configuration, not an isolation
boundary for hostile code.  This module nevertheless keeps the execution
surface deliberately small: commands are argv arrays, shell launchers and
shell control operators are rejected, paths cannot escape the repository, and
only ``{root}``, ``{artifact_dir}``, and the current interpreter ``{python}``
are expanded.  A verifier can be scheduled for the ``preflight`` phase, the
``final`` phase (the backward-compatible default), or both.

Passing a verifier never promotes a mathematical claim.  In particular, a
``numerical`` verifier remains numerical evidence and an ``exact`` verifier is
only a finite certificate for the cases it actually checks.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Mapping, Sequence


VERIFIER_MODES = {"exact", "formal", "deterministic", "numerical"}
VERIFIER_WHEN = {"preflight", "final", "both"}
VERIFIER_PHASES = {"preflight", "final"}
_REQUIRED_FIELDS = {
    "name",
    "command",
    "mode",
    "timeout_seconds",
    "expected_exit_code",
}
_OPTIONAL_FIELDS = {"when"}
_SIMPLE_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]+")
_SHELL_CONTROL_TOKEN = re.compile(
    r"^(?:&&|\|\||[|;&<>]|\d*(?:>>?|<<?|>&|<&))$"
)
_EMBEDDED_SHELL_CONTROL = re.compile(
    r"(?:^|\s)(?:&&|\|\||[|;<>])(?:\s|$)"
)
_SHELL_EXECUTABLES = {
    "bash",
    "busybox",
    "cmd",
    "cmd.exe",
    "command",
    "cscript",
    "cscript.exe",
    "dash",
    "fish",
    "ksh",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
    "sh",
    "wscript",
    "wscript.exe",
    "zsh",
}
_DISALLOWED_SCRIPT_SUFFIXES = {".bat", ".cmd", ".com", ".ps1", ".sh"}
_APPROVED_EXTERNAL_EXECUTABLES = {
    "elan",
    "elan.exe",
    "julia",
    "julia.exe",
    "lake",
    "lake.exe",
    "lean",
    "lean.exe",
    "py",
    "py.exe",
    "pypy",
    "pypy.exe",
    "pypy3",
    "pypy3.exe",
    "python",
    "python.exe",
    "python3",
    "python3.exe",
    "sage",
    "sage.exe",
}


def _python_source_index(command: Sequence[str]) -> int | None:
    """Return the opaque Python/Sage ``-c`` source position, if any."""

    if len(command) <= 2 or command[1] != "-c":
        return None
    executable_name = Path(command[0]).name.casefold()
    if executable_name in {
        "{python}",
        "py",
        "py.exe",
        "pypy",
        "pypy.exe",
        "pypy3",
        "pypy3.exe",
        "python",
        "python.exe",
        "python3",
        "python3.exe",
        "sage",
        "sage.exe",
    }:
        return 2
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(path: Path, directory: Path) -> bool:
    """Return whether a resolved path is inside a resolved directory."""

    try:
        path.resolve().relative_to(directory.resolve())
    except (OSError, ValueError):
        return False
    return True


def _slug(value: str) -> str:
    slug = _SAFE_NAME.sub("-", value.strip()).strip(".-")
    return (slug or "verifier")[:80]


def _static_command_errors(command: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(command, list) or not command:
        return ["command must be a non-empty argv array"]
    if not all(isinstance(part, str) and part for part in command):
        return ["every command element must be a non-empty string"]

    python_source_index = _python_source_index(command)
    for index, part in enumerate(command):
        if "\x00" in part or "\r" in part or "\n" in part:
            errors.append(f"command[{index}] contains a control character")
            continue
        # Source passed directly to a trusted Python interpreter is not a
        # formatting template.  Treating f-string braces as harness
        # placeholders would corrupt ordinary verifier programs.
        if index == python_source_index:
            continue
        fields = set(_SIMPLE_PLACEHOLDER.findall(part))
        unknown = sorted(fields - {"root", "artifact_dir", "python"})
        if unknown:
            errors.append(
                f"command[{index}] uses unsupported placeholders: {unknown}"
            )
        residue = (
            part.replace("{root}", "")
            .replace("{artifact_dir}", "")
            .replace("{python}", "")
        )
        if "{" in residue or "}" in residue:
            errors.append(
                f"command[{index}] contains unsupported placeholder syntax"
            )
        if "{python}" in part and (index != 0 or part != "{python}"):
            errors.append("{python} is allowed only as the complete executable token")
        # Catch misspelled/unclosed forms of the reserved placeholders.
        for reserved in ("root", "artifact_dir", "python"):
            if "{" + reserved in part and "{" + reserved + "}" not in part:
                errors.append(
                    f"command[{index}] contains malformed {{{reserved}}} placeholder"
                )
        stripped = part.strip()
        if _SHELL_CONTROL_TOKEN.fullmatch(stripped):
            errors.append(f"command[{index}] is a shell control operator: {stripped!r}")
        elif _EMBEDDED_SHELL_CONTROL.search(part):
            errors.append(
                f"command[{index}] contains shell-style control syntax"
            )
    return errors


def validate_verifier_spec(spec: Mapping[str, Any] | Any) -> list[str]:
    """Return human-readable validation errors for one verifier specification."""

    if not isinstance(spec, Mapping):
        return ["verifier specification must be an object"]

    errors: list[str] = []
    missing = sorted(_REQUIRED_FIELDS - set(spec))
    extra = sorted(set(spec) - _REQUIRED_FIELDS - _OPTIONAL_FIELDS)
    if missing:
        errors.append(f"missing verifier fields: {missing}")
    if extra:
        errors.append(f"unsupported verifier fields: {extra}")

    name = spec.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name must be a non-empty string")
    elif len(name) > 200 or any(mark in name for mark in ("\x00", "\r", "\n", "/", "\\")):
        errors.append("name contains an unsafe path or control character")

    errors.extend(_static_command_errors(spec.get("command")))

    mode = spec.get("mode")
    if mode not in VERIFIER_MODES:
        errors.append(
            "mode must be one of exact, formal, deterministic, numerical"
        )
    timeout = spec.get("timeout_seconds")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1:
        errors.append("timeout_seconds must be an integer >= 1")
    expected = spec.get("expected_exit_code")
    if not isinstance(expected, int) or isinstance(expected, bool):
        errors.append("expected_exit_code must be an integer")
    when = spec.get("when", "final")
    if when not in VERIFIER_WHEN:
        errors.append("when must be one of preflight, final, both")
    return errors


def _expand_command(
    command: Sequence[str], *, root: Path, artifact_dir: Path
) -> list[str]:
    replacements = {
        "{root}": str(root.resolve()),
        "{artifact_dir}": str(artifact_dir.resolve()),
        "{python}": str(Path(sys.executable).resolve()),
    }
    expanded: list[str] = []
    python_source_index = _python_source_index(command)
    for index, part in enumerate(command):
        if index == python_source_index:
            expanded.append(part)
            continue
        for placeholder, value in replacements.items():
            part = part.replace(placeholder, value)
        expanded.append(part)
    return expanded


def _argument_path_candidates(argument: str) -> list[str]:
    """Extract argv fragments which can carry filesystem paths.

    This covers direct paths, ``--option=/path`` forms, and response-file
    syntax.  It intentionally does not interpret Python source supplied with
    ``-c``; task verifier code is trusted repository configuration.
    """

    candidates = [argument]
    if "=" in argument and argument.startswith("-"):
        candidates.append(argument.split("=", 1)[1])
    if argument.startswith("@") and len(argument) > 1:
        candidates.append(argument[1:])
    return candidates


def _expanded_command_errors(
    command: Sequence[str], *, root: Path, artifact_dir: Path
) -> list[str]:
    errors: list[str] = []
    executable = command[0]
    executable_path = Path(executable)
    executable_name = executable_path.name.casefold()

    if executable_name in _SHELL_EXECUTABLES:
        errors.append(f"shell executable is not allowed: {executable!r}")
    if executable_path.suffix.casefold() in _DISALLOWED_SCRIPT_SUFFIXES:
        errors.append(f"shell-backed executable is not allowed: {executable!r}")
    if any(mark in executable for mark in ("`", "$", "%", "|", "&", ";", "<", ">")):
        errors.append(f"executable contains unsafe shell syntax: {executable!r}")

    has_separator = "/" in executable or "\\" in executable
    if executable_path.is_absolute() or has_separator:
        resolved_executable = (
            executable_path.resolve()
            if executable_path.is_absolute()
            else (root / executable_path).resolve()
        )
        if not _inside(resolved_executable, root):
            discovered = shutil.which(executable_name)
            trusted_external = resolved_executable == Path(sys.executable).resolve()
            if discovered:
                trusted_external = trusted_external or (
                    Path(discovered).resolve() == resolved_executable
                )
            if executable_name not in _APPROVED_EXTERNAL_EXECUTABLES or not trusted_external:
                errors.append(
                    "external executable must be the current Python interpreter or the "
                    "resolved PATH entry for an approved Python/Sage/Lean tool"
                )
        if not resolved_executable.is_file():
            errors.append(f"executable does not exist: {executable!r}")
    elif executable_name not in _APPROVED_EXTERNAL_EXECUTABLES:
        errors.append(
            "bare executable is not approved; use Python, Sage, Lean/Lake, "
            "or a repository-contained executable path"
        )

    python_source_index = 2 if len(command) > 2 and command[1] == "-c" else None
    for index, argument in enumerate(command[1:], start=1):
        if index == python_source_index:
            continue
        for candidate in _argument_path_candidates(argument):
            if not candidate or "://" in candidate:
                continue
            candidate_path = Path(candidate)
            parts = PurePath(candidate.replace("\\", "/")).parts
            if ".." in parts:
                errors.append(f"command[{index}] contains parent-path traversal")
                break
            path_like = (
                candidate_path.is_absolute()
                or bool(candidate_path.anchor)
                or "/" in candidate
                or "\\" in candidate
            )
            if path_like:
                resolved_candidate = (
                    candidate_path.resolve()
                    if candidate_path.is_absolute() or candidate_path.anchor
                    else (root / candidate_path).resolve()
                )
                if not _inside(resolved_candidate, root):
                    errors.append(
                        f"command[{index}] uses a path outside repository root"
                    )
                    break

    if not _inside(artifact_dir, root):
        errors.append("artifact_dir must be inside repository root")
    return errors


def _empty_record(
    spec: Mapping[str, Any] | Any, index: int, phase: Any
) -> dict[str, Any]:
    values = spec if isinstance(spec, Mapping) else {}
    mode = values.get("mode")
    when = values.get("when", "final")
    return {
        "schema_version": "1.0",
        "index": index,
        "name": values.get("name", f"verifier-{index}"),
        "mode": mode if mode in VERIFIER_MODES else None,
        "when": when if isinstance(when, str) else None,
        "phase": phase if isinstance(phase, str) else None,
        "command": [],
        "expected_exit_code": values.get("expected_exit_code"),
        "exit_code": None,
        "status": "invalid",
        "passed": False,
        "timed_out": False,
        "duration_seconds": 0.0,
        "started_at": None,
        "finished_at": None,
        "stdout_path": None,
        "stderr_path": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "errors": [],
    }


def run_verifier(
    spec: Mapping[str, Any] | Any,
    *,
    root: Path,
    artifact_dir: Path,
    run_dir: Path,
    index: int = 0,
    phase: str = "final",
) -> dict[str, Any]:
    """Execute one verifier and return a JSON-serializable structured record.

    The verifier runs with ``cwd=root`` and ``shell=False``.  Its two streams
    are written under ``run_dir/verifiers`` even when it exits unsuccessfully
    or times out.
    """

    record = _empty_record(spec, index, phase)
    if phase not in VERIFIER_PHASES:
        record["errors"] = [
            "phase must be one of preflight, final"
        ]
        return record

    static_errors = validate_verifier_spec(spec)
    if static_errors:
        record["errors"] = static_errors
        return record

    when = spec.get("when", "final")
    if when != "both" and when != phase:
        record["status"] = "skipped"
        return record

    root = root.resolve()
    artifact_dir = artifact_dir.resolve()
    run_dir = run_dir.resolve()

    path_errors: list[str] = []
    if not root.is_dir():
        path_errors.append("repository root does not exist or is not a directory")
    if not _inside(run_dir, root):
        path_errors.append("run_dir must be inside repository root")
    if not _inside(artifact_dir, root):
        path_errors.append("artifact_dir must be inside repository root")
    if path_errors:
        record["errors"] = path_errors
        return record

    command = _expand_command(spec["command"], root=root, artifact_dir=artifact_dir)
    record["command"] = command
    errors = _expanded_command_errors(command, root=root, artifact_dir=artifact_dir)
    if errors:
        record["errors"] = errors
        return record

    logs_dir = run_dir / "verifiers"
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        record["errors"] = [f"cannot create verifier log directory: {error}"]
        return record
    if not _inside(logs_dir, run_dir):
        record["errors"] = ["verifier log directory resolves outside run_dir"]
        return record
    phase_prefix = "preflight-" if phase == "preflight" else ""
    basename = f"{index:03d}-{phase_prefix}{_slug(str(spec['name']))}"
    stdout_path = logs_dir / f"{basename}.stdout.log"
    stderr_path = logs_dir / f"{basename}.stderr.log"
    for stream_path in (stdout_path, stderr_path):
        if stream_path.exists() or stream_path.is_symlink() or not _inside(stream_path, logs_dir):
            record["errors"] = ["verifier stream path already exists or is unsafe"]
            return record
    record["stdout_path"] = stdout_path.relative_to(root).as_posix()
    record["stderr_path"] = stderr_path.relative_to(root).as_posix()

    record["started_at"] = _utc_now()
    started = time.monotonic()
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            completed = subprocess.run(
                command,
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                timeout=spec["timeout_seconds"],
                check=False,
                shell=False,
                env=os.environ.copy(),
            )
        record["exit_code"] = completed.returncode
        if completed.returncode == spec["expected_exit_code"]:
            record["status"] = "passed"
            record["passed"] = True
        else:
            record["status"] = "failed"
            record["errors"] = [
                f"exit code {completed.returncode} did not match expected "
                f"{spec['expected_exit_code']}"
            ]
    except subprocess.TimeoutExpired:
        record["status"] = "timed_out"
        record["timed_out"] = True
        record["errors"] = [
            f"verifier exceeded timeout of {spec['timeout_seconds']} seconds"
        ]
    except OSError as error:
        record["status"] = "launch_error"
        record["errors"] = [f"could not launch verifier: {error}"]
    finally:
        record["duration_seconds"] = round(time.monotonic() - started, 6)
        record["finished_at"] = _utc_now()
    for label, path in (("stdout", stdout_path), ("stderr", stderr_path)):
        if path.is_file() and _inside(path, logs_dir):
            record[f"{label}_bytes"] = path.stat().st_size
            record[f"{label}_sha256"] = _file_sha256(path)
    return record


def run_verifiers(
    specs: Sequence[Mapping[str, Any]],
    *,
    root: Path,
    artifact_dir: Path,
    run_dir: Path,
    phase: str = "final",
) -> tuple[list[dict[str, Any]], list[str]]:
    """Run applicable verifier specs and return records plus aggregated errors.

    Verifiers without an explicit ``when`` retain the historical behavior and
    run only in the default ``final`` phase.  Non-applicable valid specs are
    omitted from the returned records; invalid specs remain visible so task
    configuration errors cannot be hidden by phase filtering.
    """

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if phase not in VERIFIER_PHASES:
        return [], ["phase must be one of preflight, final"]
    for index, spec in enumerate(specs):
        record = run_verifier(
            spec,
            root=root,
            artifact_dir=artifact_dir,
            run_dir=run_dir,
            index=index,
            phase=phase,
        )
        if record["status"] == "skipped":
            continue
        records.append(record)
        label = record.get("name", f"verifier-{index}")
        errors.extend(f"verifier {label}: {error}" for error in record["errors"])
    return records, errors
