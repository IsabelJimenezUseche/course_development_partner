#!/usr/bin/env python3
"""Validate a Markdown or CSV assessment blueprint.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: assessment-quality gaps detected
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _tabular import (
    COGNITIVE_DEMANDS,
    cognitive_demand_vocabulary,
    find_cycles,
    load_table,
    normalize,
    normalized_mapping,
    normalized_row,
    parse_cognitive_demand,
    parse_identifier_list,
    parse_positive_finite,
)


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
VALID_STATUSES = {"draft", "review", "approved", "blocked", "retired"}
VALID_EVIDENCE_LEVELS = {
    "classroom-reviewed", "expert-reviewed", "piloted", "reliability-examined", "formally-validated"
}
ACTIVE_ALIGNMENT_STATUSES = {"draft", "review", "approved", "blocked"}


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
    parser.add_argument(
        "--alignment-map",
        type=Path,
        help="Optional alignment map that bounds and validates the declared assessed-outcome scope",
    )
    return parser.parse_args()


def load(path: Path) -> tuple[str, list[str], list[dict[str, str]]]:
    return load_table(path, REQUIRED)


def evidence_level(text: str, rows: list[dict[str, str]], mapping: dict[str, str]) -> str:
    matches = re.findall(
        r"^\s*-\s*Evidence level claimed:\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.I,
    )
    if len(matches) > 1:
        raise ValueError("Markdown contains duplicate evidence-level claims")
    markdown_value = normalize(matches[0]).replace(" ", "-") if matches else ""
    column_value = ""
    if "evidence level claimed" in mapping:
        values = {
            normalize(row.get(mapping["evidence level claimed"], "")).replace(" ", "-")
            for row in rows
            if row.get(mapping["evidence level claimed"], "").strip()
        }
        if len(values) > 1:
            raise ValueError("CSV contains conflicting evidence-level claims")
        column_value = next(iter(values), "")
    if markdown_value and column_value and markdown_value != column_value:
        raise ValueError("Markdown and table evidence-level claims conflict")
    return markdown_value or column_value


def assessed_outcome_scope(
    text: str,
    rows: list[dict[str, str]],
    mapping: dict[str, str],
) -> str:
    matches = re.findall(
        r"^\s*-\s*Assessed outcome scope:\s*(.+?)\s*$",
        text,
        re.MULTILINE | re.I,
    )
    if len(matches) > 1:
        raise ValueError("Markdown contains duplicate assessed-outcome scopes")
    markdown_value = matches[0].strip() if matches else ""
    column_values: dict[str, str] = {}
    if "assessed outcome scope" in mapping:
        for row in rows:
            value = row.get(mapping["assessed outcome scope"], "").strip()
            if value:
                column_values[normalize(value)] = value
        if len(column_values) > 1:
            raise ValueError("CSV contains conflicting assessed-outcome scopes")
    column_value = next(iter(column_values.values()), "")
    if (
        markdown_value
        and column_value
        and normalize(markdown_value) != normalize(column_value)
    ):
        raise ValueError("Markdown and table assessed-outcome scopes conflict")
    return markdown_value or column_value


def alignment_outcome_demands(path: Path) -> dict[str, str]:
    """Map each active aligned outcome ID to its declared cognitive-demand token."""
    required = (
        "outcome id", "observable learning outcome", "cognitive demand",
        "evidence of learning", "learning mechanism", "learning activity/support",
        "feedback or assessment", "status"
    )
    _, headers, rows = load_table(path, required)
    mapping = normalized_mapping(headers, required)
    demands: dict[str, str] = {}
    for raw in rows:
        row = normalized_row(raw, mapping)
        if normalize(row["status"]) not in ACTIVE_ALIGNMENT_STATUSES:
            continue
        value = row["outcome id"]
        if not value:
            continue
        for outcome in parse_identifier_list(value, field_name="outcome"):
            demands[outcome] = normalize(row["cognitive demand"])
    return demands


def validate(
    path: Path,
    required_outcomes: list[str],
    allow_formal_validation: bool,
    alignment_map: Path | None = None,
) -> tuple[list[str], list[str]]:
    try:
        text, headers, raw_rows = load(path)
        mapping = normalized_mapping(headers, REQUIRED)
        claimed_level = evidence_level(text, raw_rows, mapping)
        scope_value = assessed_outcome_scope(text, raw_rows, mapping)
        outcome_demands = alignment_outcome_demands(alignment_map) if alignment_map else {}
        derived_outcomes = set(outcome_demands)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []
    if not raw_rows:
        return [], ["Assessment blueprint contains no data rows"]

    issues: list[str] = []
    seen_items: set[str] = set()
    active_items: set[str] = set()
    represented_outcomes: set[str] = set()
    dependency_values: dict[str, str] = {}
    scoped_outcomes: set[str] = set()
    scope_resolved = False
    highest_item_demand: dict[str, int] = {}

    normalized_scope = normalize(scope_value).replace(" ", "-")
    if not scope_value:
        issues.append("Missing assessed outcome scope")
    elif normalized_scope == "all-active":
        if alignment_map is not None:
            scoped_outcomes = set(derived_outcomes)
            scope_resolved = True
            if not scoped_outcomes:
                issues.append(
                    "Assessed outcome scope all-active contains no active aligned outcomes"
                )
        elif required_outcomes:
            scoped_outcomes = {normalize(outcome) for outcome in required_outcomes}
            scope_resolved = True
        else:
            issues.append(
                "Assessed outcome scope all-active requires an alignment map or "
                "explicit --required-outcome values"
            )
    else:
        try:
            scoped_outcomes = parse_identifier_list(
                scope_value,
                field_name="assessed outcome scope",
            )
            if not scoped_outcomes:
                issues.append("Assessed outcome scope contains no outcome IDs")
            else:
                scope_resolved = True
        except ValueError as exc:
            issues.append(str(exc))

    if alignment_map is not None:
        for outcome in sorted(scoped_outcomes - derived_outcomes):
            issues.append(
                f"Assessed outcome scope is not active in the alignment map: {outcome.upper()}"
            )

    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        item_id = row["item id"]
        if not item_id and any(row.values()):
            issues.append(f"Row {row_number}: assessment content has no item ID")
            continue
        if not item_id:
            issues.append(f"Row {row_number}: empty row")
            continue

        normalized_id = normalize(item_id)
        try:
            ids = parse_identifier_list(item_id, field_name="item")
            if len(ids) != 1:
                issues.append(f"Row {row_number}: item ID must contain exactly one identifier")
            normalized_id = next(iter(ids))
        except ValueError as exc:
            issues.append(f"Row {row_number}: {exc}")
        if normalized_id in seen_items:
            issues.append(f"Row {row_number}: duplicate item ID {item_id}")
        seen_items.add(normalized_id)

        for field_name in REQUIRED[1:]:
            if not row[field_name]:
                issues.append(f"Row {row_number} ({item_id}): missing {field_name}")

        status = normalize(row["status"])
        if status and status not in VALID_STATUSES:
            issues.append(f"Row {row_number} ({item_id}): unknown status {row['status']}")
        item_demand = parse_cognitive_demand(row["cognitive demand"])
        if row["cognitive demand"] and item_demand is None:
            issues.append(
                f"Row {row_number} ({item_id}): unknown cognitive demand "
                f"{row['cognitive demand']}; use one of {cognitive_demand_vocabulary()}"
            )
        if status != "retired":
            active_items.add(normalized_id)
            if row["outcome(s)"]:
                try:
                    item_outcomes = parse_identifier_list(
                        row["outcome(s)"], field_name="outcome"
                    )
                    represented_outcomes.update(item_outcomes)
                    if item_demand is not None:
                        for outcome in item_outcomes:
                            highest_item_demand[outcome] = max(
                                highest_item_demand.get(outcome, 0), item_demand
                            )
                except ValueError as exc:
                    issues.append(f"Row {row_number} ({item_id}): {exc}")
        if row["expected time (min)"] and parse_positive_finite(row["expected time (min)"]) is None:
            issues.append(f"Row {row_number} ({item_id}): expected time must be a positive number")
        if row["points"] and parse_positive_finite(row["points"]) is None:
            issues.append(f"Row {row_number} ({item_id}): points must be a positive number")
        if status != "retired":
            dependency_values[normalized_id] = row["dependency"]

    graph: dict[str, set[str]] = {}
    for item_id, value in dependency_values.items():
        if normalize(value) == "independent":
            graph[item_id] = set()
            continue
        try:
            dependencies = parse_identifier_list(value, field_name="dependency")
        except ValueError as exc:
            issues.append(f"{item_id}: {exc}")
            continue
        graph[item_id] = dependencies
        for dependency in dependencies:
            if dependency not in active_items:
                issues.append(f"{item_id}: unknown or retired dependency item {dependency}")
    for cycle in find_cycles(graph):
        issues.append(f"Circular item dependencies: {cycle}")

    if not active_items:
        issues.append("Assessment blueprint contains no active items")

    if scope_resolved:
        for outcome in sorted(represented_outcomes - scoped_outcomes):
            issues.append(f"Assessment item uses outcome outside declared scope: {outcome.upper()}")

    all_required = {normalize(outcome) for outcome in required_outcomes} | scoped_outcomes
    for outcome in sorted(all_required):
        if outcome not in represented_outcomes:
            issues.append(f"Required outcome is not sampled: {outcome.upper()}")

    # Cognitive-demand match. A blueprint may legitimately contain items below the
    # outcome's demand as scaffolding, so compare at the outcome level: report only
    # when no active item reaches the demand the alignment map declares.
    rank_names = {rank: name for name, rank in COGNITIVE_DEMANDS.items()}
    for outcome in sorted(represented_outcomes & set(outcome_demands)):
        outcome_rank = parse_cognitive_demand(outcome_demands[outcome])
        if outcome_rank is None:
            continue
        item_rank = highest_item_demand.get(outcome)
        if item_rank is None:
            continue
        if item_rank < outcome_rank:
            issues.append(
                f"{outcome.upper()}: highest active item demand {rank_names[item_rank]} is below "
                f"the aligned outcome demand {rank_names[outcome_rank]}"
            )

    if not claimed_level:
        issues.append("Missing evidence level claimed")
    elif claimed_level not in VALID_EVIDENCE_LEVELS:
        issues.append(f"Unknown evidence level claimed: {claimed_level}")
    if claimed_level == "formally-validated" and not allow_formal_validation:
        issues.append(
            "Formal-validation claim requires verified external evidence and "
            "--allow-formal-validation"
        )

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(
        args.path, args.required_outcome, args.allow_formal_validation, args.alignment_map
    )
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"GAP: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print(f"OK: blueprint structural and declared-coverage checks passed; manual validity review still required: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
