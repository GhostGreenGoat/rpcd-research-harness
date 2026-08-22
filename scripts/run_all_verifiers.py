#!/usr/bin/env python3
"""Run unit tests and the deterministic finite RPCD certificate."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [sys.executable, "scripts/verify_rpcd_identities.py"],
        [
            sys.executable,
            "scripts/search_rpcd_counterexample.py",
            "--n",
            "3",
            "--sigma",
            "0.4",
            "--samples",
            "3",
            "--seed",
            "7",
        ],
    ]
    for command in commands:
        completed = subprocess.run(command, check=False)
        if completed.returncode != 0:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
