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


REQUIRED_H2 = (
    "course context",
    "intended learning",
    "access, participation, and belonging",
    "constraints",
    "implementation load",
    "collaboration",
    "status",
)
REQUIRED_H3 = ("confirmed", "assumed", "open", "current phase", "next decision")
PROFILE_REQUIRED_FIELDS = {
    "establish": (
        "engagement tier", "course or module", "learning outcomes", "interaction level",
        "requested artifacts"
    ),
    "produce": (
        "engagement tier", "course or module", "learning outcomes", "technology and format",
        "interaction level", "requested artifacts", "minimum viable fallback"
    ),
    "handoff": (
        "engagement tier", "course or module", "learning outcomes", "technology and format",
        "interaction level", "requested artifacts", "minimum viable fallback",
        "accessibility contact, review, procurement, or exception process"
    ),
}
VALID_ENGAGEMENT_TIERS = {"focused", "project", "course"}


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
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILE_REQUIRED_FIELDS),
        default="establish",
        help="Completion profile to apply (default: establish)",
    )
    return parser.parse_args()


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def section_body(text: str, heading: str, level: int) -> str:
    hashes = "#" * level
    pattern = rf"^{hashes}\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^#{{1,{level}}}\s+|\Z)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return match.group("body").strip() if match else ""


def field_values(text: str) -> tuple[dict[str, str], set[str]]:
    values: dict[str, str] = {}
    duplicates: set[str] = set()
    for match in re.finditer(r"^\s*-\s+([^:\n]+):\s*(.*?)\s*$", text, flags=re.MULTILINE):
        field = normalize_heading(match.group(1))
        if field in values:
            duplicates.add(field)
        values[field] = match.group(2).strip()
    return values, duplicates


def validate(path: Path, profile: str = "establish") -> tuple[list[str], list[str]]:
    if not path.is_file():
        return [f"File does not exist: {path}"], []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read {path}: {exc}"], []

    heading_records = [
        (len(match.group(1)), normalize_heading(match.group(2)))
        for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.MULTILINE)
    ]
    counts: dict[tuple[int, str], int] = {}
    for record in heading_records:
        counts[record] = counts.get(record, 0) + 1
    errors: list[str] = []
    for heading in REQUIRED_H2:
        if (2, heading) not in counts:
            errors.append(f"Missing required level-2 heading: {heading}")
        elif counts[(2, heading)] > 1:
            errors.append(f"Duplicate required heading: {heading}")
    for heading in REQUIRED_H3:
        if (3, heading) not in counts:
            errors.append(f"Missing required level-3 heading: {heading}")
        elif counts[(3, heading)] > 1:
            errors.append(f"Duplicate required heading: {heading}")

    status_start = re.search(r"^##\s+Status\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if status_start:
        trailing = text[status_start.end() :]
        next_h2 = re.search(r"^##\s+", trailing, flags=re.MULTILINE)
        status_text = trailing[: next_h2.start()] if next_h2 else trailing
        for heading in REQUIRED_H3:
            if not re.search(rf"^###\s+{re.escape(heading)}\s*$", status_text, flags=re.I | re.M):
                errors.append(f"Status subsection is outside Status: {heading}")

    incomplete: list[str] = []
    placeholder_patterns = (
        (r"\b(?:TODO|TBD)\b", "Contains TODO/TBD marker"),
        (r"\[[^\]\n]+\](?!\()", "Contains bracketed placeholder"),
        (r"^\s*-\s*$", "Contains an empty list item"),
        (r"^\s*-\s+[^:\n]+:\s*$", "Contains an unanswered field"),
    )
    for pattern, message in placeholder_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            incomplete.append(message)

    for heading in REQUIRED_H3:
        body = section_body(text, heading, 3)
        if (3, heading) in counts and not re.search(r"\w", re.sub(r"^[\s-]+$", "", body)):
            incomplete.append(f"Section is empty: {heading}")

    values, duplicate_fields = field_values(text)
    tracked_fields = {
        field
        for required_fields in PROFILE_REQUIRED_FIELDS.values()
        for field in required_fields
    }
    for field in sorted(duplicate_fields & tracked_fields):
        errors.append(f"Duplicate scalar field: {field}")
    for field in PROFILE_REQUIRED_FIELDS[profile]:
        value = values.get(field, "")
        if not value:
            incomplete.append(f"Required field is unanswered for {profile}: {field}")
        elif normalize_heading(value) in {"n/a", "na", "not applicable"}:
            incomplete.append(f"Not-applicable field requires a rationale: {field}")

    engagement_tier = normalize_heading(values.get("engagement tier", ""))
    if engagement_tier and engagement_tier not in VALID_ENGAGEMENT_TIERS:
        incomplete.append(f"Unknown engagement tier: {values['engagement tier']}")

    return errors, sorted(set(incomplete))


def main() -> int:
    args = parse_args()
    errors, incomplete = validate(args.path, args.profile)
    for item in errors:
        print(f"ERROR: {item}")
    for item in incomplete:
        print(f"INCOMPLETE: {item}")
    if errors:
        return 1
    if incomplete:
        return 2
    print(
        f"OK: structurally complete course-design brief for profile {args.profile}; "
        f"manual design review still required: {args.path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
