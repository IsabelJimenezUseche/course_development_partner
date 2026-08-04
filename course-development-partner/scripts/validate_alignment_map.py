#!/usr/bin/env python3
"""Validate a Markdown or CSV outcome-alignment map.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: alignment gaps detected
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _tabular import (
    emit_report,
    cognitive_demand_vocabulary,
    load_table,
    normalize,
    normalized_mapping,
    normalized_row,
    parse_cognitive_demand,
    parse_identifier_list,
)


REQUIRED = (
    "outcome id",
    "observable learning outcome",
    "cognitive demand",
    "evidence of learning",
    "learning mechanism",
    "learning activity/support",
    "feedback or assessment",
    "status",
)
VALID_STATUSES = {"draft", "review", "approved", "blocked", "retired"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required columns and outcome alignment in a Markdown or CSV map.",
        epilog=(
            "Examples:\n"
            "  validate_alignment_map.py alignment-map.md\n"
            "  validate_alignment_map.py alignment-map.csv"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to alignment-map.md or a CSV equivalent")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def validate(path: Path) -> tuple[list[str], list[str]]:
    try:
        _, headers, raw_rows = load_table(path, REQUIRED)
        mapping = normalized_mapping(headers, REQUIRED)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []
    if not raw_rows:
        return [], ["Alignment map contains no data rows"]

    issues: list[str] = []
    seen_ids: set[str] = set()
    active_ids: set[str] = set()
    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        outcome_id = row["outcome id"]
        outcome = row["observable learning outcome"]
        cognitive_demand = row["cognitive demand"]
        evidence = row["evidence of learning"]
        learning_mechanism = row["learning mechanism"]
        activity = row["learning activity/support"]
        assessment = row["feedback or assessment"]
        status = row["status"]

        if status and normalize(status) not in VALID_STATUSES:
            issues.append(f"Row {row_number} ({outcome_id or 'no outcome ID'}): unknown status {status}")

        if cognitive_demand and parse_cognitive_demand(cognitive_demand) is None:
            issues.append(
                f"Row {row_number} ({outcome_id or 'no outcome ID'}): unknown cognitive demand "
                f"{cognitive_demand}; use one of {cognitive_demand_vocabulary()}"
            )

        if not outcome_id and any(row.values()):
            issues.append(f"Row {row_number}: activity or assessment has no outcome ID")
        if outcome_id:
            try:
                normalized_ids = parse_identifier_list(outcome_id, field_name="outcome")
            except ValueError as exc:
                issues.append(f"Row {row_number}: {exc}")
                normalized_ids = {normalize(outcome_id)}
            if len(normalized_ids) != 1:
                issues.append(f"Row {row_number}: outcome ID must contain exactly one identifier")
            normalized_id = next(iter(normalized_ids))
            if normalized_id in seen_ids:
                issues.append(f"Row {row_number}: duplicate outcome ID {outcome_id}")
            seen_ids.add(normalized_id)
            if normalize(status) != "retired":
                active_ids.add(normalized_id)
            for field_name, value in (
                ("observable learning outcome", outcome),
                ("cognitive demand", cognitive_demand),
                ("evidence of learning", evidence),
                ("learning mechanism", learning_mechanism),
                ("learning activity/support", activity),
                ("feedback or assessment", assessment),
                ("status", status),
            ):
                if not value:
                    issues.append(f"Row {row_number} ({outcome_id}): missing {field_name}")
        elif not any(row.values()):
            issues.append(f"Row {row_number}: empty row")

    if not active_ids:
        issues.append("Alignment map contains no active outcomes")

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path)
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="GAP",
        ok_message=f"structurally complete alignment map; manual alignment review still required: {args.path}",
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
