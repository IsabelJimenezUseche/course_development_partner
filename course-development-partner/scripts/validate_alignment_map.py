#!/usr/bin/env python3
"""Validate a Markdown or CSV outcome-alignment map.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: alignment gaps detected
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


REQUIRED = (
    "outcome id",
    "observable learning outcome",
    "evidence of learning",
    "learning activity/support",
    "feedback or assessment",
    "status",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required columns and outcome alignment in a Markdown or CSV map."
    )
    parser.add_argument("path", type=Path, help="Path to alignment-map.md or a CSV equivalent")
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def markdown_rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    for index in range(len(lines) - 1):
        header = [cell.strip() for cell in lines[index].strip("|").split("|")]
        separator = [cell.strip() for cell in lines[index + 1].strip("|").split("|")]
        if len(header) == len(separator) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            rows: list[dict[str, str]] = []
            for line in lines[index + 2 :]:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if len(cells) != len(header):
                    break
                rows.append(dict(zip(header, cells)))
            return header, rows
    raise ValueError("No Markdown table found")


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValueError(f"File does not exist: {path}")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header")
            return reader.fieldnames, [dict(row) for row in reader]
    return markdown_rows(path.read_text(encoding="utf-8"))


def validate(path: Path) -> tuple[list[str], list[str]]:
    try:
        headers, raw_rows = load_rows(path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    mapping = {normalize(header): header for header in headers}
    missing = [column for column in REQUIRED if column not in mapping]
    if missing:
        return [f"Missing required column: {column}" for column in missing], []
    if not raw_rows:
        return [], ["Alignment map contains no data rows"]

    issues: list[str] = []
    seen_ids: set[str] = set()
    for row_number, raw in enumerate(raw_rows, start=1):
        row = {key: (raw.get(original) or "").strip() for key, original in mapping.items()}
        outcome_id = row["outcome id"]
        outcome = row["observable learning outcome"]
        evidence = row["evidence of learning"]
        activity = row["learning activity/support"]
        assessment = row["feedback or assessment"]
        status = row["status"]

        if not outcome_id and any((outcome, evidence, activity, assessment)):
            issues.append(f"Row {row_number}: activity or assessment has no outcome ID")
        if outcome_id:
            normalized_id = normalize(outcome_id)
            if normalized_id in seen_ids:
                issues.append(f"Row {row_number}: duplicate outcome ID {outcome_id}")
            seen_ids.add(normalized_id)
            for field_name, value in (
                ("observable learning outcome", outcome),
                ("evidence of learning", evidence),
                ("learning activity/support", activity),
                ("feedback or assessment", assessment),
                ("status", status),
            ):
                if not value:
                    issues.append(f"Row {row_number} ({outcome_id}): missing {field_name}")
        elif not any(row.values()):
            issues.append(f"Row {row_number}: empty row")

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path)
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
