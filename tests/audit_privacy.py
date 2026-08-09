#!/usr/bin/env python3
"""Scan release files for likely personal data and secret material.

This is a deterministic screening step, not proof that a repository is safe.
Exit codes: 0 pass, 1 scanner/input error, 2 candidate finding.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".csv", ".tsv", ".txt"}
PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "US phone-like number": re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)"),
    "US SSN-like number": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "credential assignment": re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"\n]{8,}['\"]",
        re.I,
    ),
}


def files_to_scan() -> list[Path]:
    paths = [ROOT / "README.md"]
    paths.extend((ROOT / "course-development-partner").rglob("*"))
    paths.extend((ROOT / "tests").rglob("*"))
    return sorted(
        {
            path
            for path in paths
            if path.is_file()
            and path.suffix.lower() in TEXT_SUFFIXES
            and "__pycache__" not in path.parts
        }
    )


def scan() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    findings: list[str] = []
    for path in files_to_scan():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read {path.relative_to(ROOT)}: {exc}")
            continue
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: candidate {label}")
    return errors, findings


def main() -> int:
    errors, findings = scan()
    for item in errors:
        print(f"ERROR: {item}")
    for item in findings:
        print(f"FINDING: {item}")
    if errors:
        return 1
    if findings:
        return 2
    print("OK: no candidate personal-data or secret patterns found; human review still required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
