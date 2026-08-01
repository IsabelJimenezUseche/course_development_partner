#!/usr/bin/env python3
"""Validate a portable course-design brief.

Exit codes:
  0: structurally complete with no unresolved placeholders
  1: file or structural error
  2: structurally valid but incomplete
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "course context",
    "intended learning",
    "constraints",
    "collaboration",
    "status",
    "confirmed",
    "assumed",
    "open",
    "current phase",
    "next decision",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required sections and completion state in course-design-brief.md.",
        epilog=(
            "Example:\n"
            "  validate_design_state.py course-design-brief.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to a Markdown course-design brief")
    return parser.parse_args()


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def validate(path: Path) -> tuple[list[str], list[str]]:
    if not path.is_file():
        return [f"File does not exist: {path}"], []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read {path}: {exc}"], []

    headings = {
        normalize_heading(match.group(1))
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE)
    }
    errors = [
        f"Missing required heading: {heading}"
        for heading in REQUIRED_HEADINGS
        if heading not in headings
    ]

    incomplete: list[str] = []
    placeholder_patterns = (
        (r"\b(?:TODO|TBD)\b", "Contains TODO/TBD marker"),
        (r"\[(?:insert|replace|describe)[^\]]*\]", "Contains bracketed placeholder"),
        (r"^\s*-\s*$", "Contains an empty list item"),
        (r"^\s*-\s+[^:\n]+:\s*$", "Contains an unanswered field"),
    )
    for pattern, message in placeholder_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            incomplete.append(message)

    for heading in ("current phase", "next decision"):
        pattern = rf"^###\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^###\s+|\Z)"
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if match and not re.search(r"\w", re.sub(r"^[\s-]+$", "", match.group("body"))):
            incomplete.append(f"Section is empty: {heading}")

    return errors, sorted(set(incomplete))


def main() -> int:
    args = parse_args()
    errors, incomplete = validate(args.path)
    for item in errors:
        print(f"ERROR: {item}")
    for item in incomplete:
        print(f"INCOMPLETE: {item}")
    if errors:
        return 1
    if incomplete:
        return 2
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
