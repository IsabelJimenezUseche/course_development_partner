#!/usr/bin/env python3
"""Validate a Markdown or CSV assessment blueprint.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: assessment-quality gaps detected
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


REQUIRED = (
    "item id",
    "outcome(s)",
    "intended interpretation/use",
    "evidence claim",
    "cognitive demand",
    "item type",
    "dependency",
    "expected time (min)",
    "points",
    "construct-irrelevant barriers",
    "status",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate completeness, coverage, and claims in an assessment blueprint.",
        epilog=(
            "Examples:\n"
            "  validate_assessment_blueprint.py assessment-blueprint.md\n"
            "  validate_assessment_blueprint.py blueprint.csv --required-outcome LO-1\n"
            "  validate_assessment_blueprint.py blueprint.md --allow-formal-validation"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to assessment-blueprint.md or CSV")
    parser.add_argument(
        "--required-outcome",
        action="append",
        default=[],
        help="Outcome ID that must be represented; repeat as needed",
    )
    parser.add_argument(
        "--allow-formal-validation",
        action="store_true",
        help="Allow a formal-validation claim after external evidence has been verified",
    )
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def markdown_rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    for index in range(len(lines) - 1):
        header = [cell.strip() for cell in lines[index].strip("|").split("|")]
        separator = [cell.strip() for cell in lines[index + 1].strip("|").split("|")]
        if len(header) == len(separator) and all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in separator
        ):
            rows: list[dict[str, str]] = []
            for line in lines[index + 2 :]:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if len(cells) != len(header):
                    break
                rows.append(dict(zip(header, cells)))
            return header, rows
    raise ValueError("No Markdown table found")


def load(path: Path) -> tuple[str, list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValueError(f"File does not exist: {path}")
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header")
            return text, reader.fieldnames, [dict(row) for row in reader]
    headers, rows = markdown_rows(text)
    return text, headers, rows


def positive_number(value: str) -> bool:
    try:
        return float(value) > 0
    except ValueError:
        return False


def outcome_tokens(value: str) -> set[str]:
    return {normalize(token) for token in re.findall(r"[A-Za-z]+-[A-Za-z0-9_-]+", value)}


def evidence_level(text: str) -> str:
    match = re.search(r"^\s*-\s*Evidence level claimed:\s*(.+?)\s*$", text, re.MULTILINE | re.I)
    return normalize(match.group(1)) if match else ""


def validate(
    path: Path, required_outcomes: list[str], allow_formal_validation: bool
) -> tuple[list[str], list[str]]:
    try:
        text, headers, raw_rows = load(path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    mapping = {normalize(header): header for header in headers}
    missing = [column for column in REQUIRED if column not in mapping]
    if missing:
        return [f"Missing required column: {column}" for column in missing], []
    if not raw_rows:
        return [], ["Assessment blueprint contains no data rows"]

    issues: list[str] = []
    seen_items: set[str] = set()
    represented_outcomes: set[str] = set()

    for row_number, raw in enumerate(raw_rows, start=1):
        row = {key: (raw.get(original) or "").strip() for key, original in mapping.items()}
        item_id = row["item id"]
        if not item_id and any(row.values()):
            issues.append(f"Row {row_number}: assessment content has no item ID")
            continue
        if not item_id:
            issues.append(f"Row {row_number}: empty row")
            continue

        normalized_id = normalize(item_id)
        if normalized_id in seen_items:
            issues.append(f"Row {row_number}: duplicate item ID {item_id}")
        seen_items.add(normalized_id)

        for field_name in REQUIRED[1:]:
            if not row[field_name]:
                issues.append(f"Row {row_number} ({item_id}): missing {field_name}")

        represented_outcomes.update(outcome_tokens(row["outcome(s)"]))
        if row["expected time (min)"] and not positive_number(row["expected time (min)"]):
            issues.append(f"Row {row_number} ({item_id}): expected time must be a positive number")
        if row["points"] and not positive_number(row["points"]):
            issues.append(f"Row {row_number} ({item_id}): points must be a positive number")

    for outcome in required_outcomes:
        if normalize(outcome) not in represented_outcomes:
            issues.append(f"Required outcome is not sampled: {outcome}")

    if evidence_level(text) == "formally validated" and not allow_formal_validation:
        issues.append(
            "Formal-validation claim requires verified external evidence and "
            "--allow-formal-validation"
        )

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(
        args.path, args.required_outcome, args.allow_formal_validation
    )
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"GAP: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
