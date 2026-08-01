#!/usr/bin/env python3
"""Validate a Markdown or CSV course curriculum map.

Exit codes:
  0: valid and coherent
  1: file, parsing, or structural error
  2: coherence or workload gaps detected
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from _tabular import (
    find_cycles,
    load_table,
    normalize,
    normalized_mapping,
    normalized_row,
    parse_identifier_list,
    parse_positive_finite,
)


REQUIRED = (
    "sequence",
    "module/week",
    "outcome id",
    "developmental stage",
    "outcome prerequisites",
    "learning experience/evidence",
    "feedback/assessment",
    "expected student workload (hours)",
    "status",
)
ALLOWED_STAGES = {"introduce", "practice", "master", "assess"}
VALID_STATUSES = {"draft", "review", "approved", "blocked", "retired"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate prerequisite flow, outcome development, and workload in a course map.",
        epilog=(
            "Examples:\n"
            "  validate_course_curriculum_map.py course-curriculum-map.md\n"
            "  validate_course_curriculum_map.py map.csv --max-hours-per-module 8"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to course-curriculum-map.md or CSV")
    parser.add_argument(
        "--max-hours-per-module",
        type=float,
        help="Optional maximum summed student workload for a module/week",
    )
    return parser.parse_args()


def parse_prerequisites(value: str) -> tuple[set[str], bool, list[str]]:
    internal: set[str] = set()
    has_external = False
    invalid: list[str] = []
    for token in (part.strip() for part in re.split(r"[;,]", value) if part.strip()):
        normalized = normalize(token)
        if normalized == "none":
            continue
        if normalized.startswith("external:"):
            has_external = True
            if not token.split(":", 1)[1].strip():
                invalid.append(token)
            continue
        try:
            internal.update(parse_identifier_list(token, field_name="prerequisite outcome"))
        except ValueError:
            invalid.append(token)
    return internal, has_external, invalid


def validate(path: Path, max_hours: float | None) -> tuple[list[str], list[str]]:
    try:
        _, headers, raw_rows = load_table(path, REQUIRED)
        mapping = normalized_mapping(headers, REQUIRED)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    if not raw_rows:
        return [], ["Course curriculum map contains no data rows"]

    issues: list[str] = []
    parsed_rows: list[dict[str, str]] = []
    outcome_ids: set[str] = set()
    stage_history: dict[str, set[str]] = defaultdict(set)
    graph: dict[str, set[str]] = defaultdict(set)
    workload_by_module: dict[str, float] = defaultdict(float)

    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        parsed_rows.append(row)
        outcome_id = normalize(row["outcome id"])
        row["outcome id normalized"] = outcome_id
        sequence = parse_positive_finite(row["sequence"])
        if row["sequence"] and sequence is None:
            issues.append(f"Row {row_number} ({row['outcome id'] or 'missing outcome'}): sequence must be a positive finite number")
        row["sequence normalized"] = str(sequence) if sequence is not None else ""
        if not outcome_id:
            issues.append(f"Row {row_number}: missing outcome ID")
            continue
        try:
            ids = parse_identifier_list(row["outcome id"], field_name="outcome")
            if len(ids) != 1:
                issues.append(f"Row {row_number}: outcome ID must contain exactly one identifier")
            outcome_id = next(iter(ids))
        except ValueError as exc:
            issues.append(f"Row {row_number}: {exc}")
        row["outcome id normalized"] = outcome_id
        outcome_ids.add(outcome_id)

    ordered_rows = sorted(
        enumerate(parsed_rows, start=1),
        key=lambda item: (
            float(item[1]["sequence normalized"]) if item[1]["sequence normalized"] else float("inf"),
            item[0],
        ),
    )
    current_sequence: float | None = None
    pending_stages: dict[str, set[str]] = defaultdict(set)

    for row_number, row in ordered_rows:
        outcome_id = row.get("outcome id normalized", normalize(row["outcome id"]))
        if not outcome_id:
            continue
        sequence = float(row["sequence normalized"]) if row["sequence normalized"] else None
        if sequence != current_sequence:
            for pending_outcome, stages_to_add in pending_stages.items():
                stage_history[pending_outcome].update(stages_to_add)
            pending_stages.clear()
            current_sequence = sequence
        for field_name in REQUIRED:
            if not row[field_name]:
                issues.append(f"Row {row_number} ({row['outcome id']}): missing {field_name}")

        stages = {normalize(stage) for stage in re.split(r"[;,/]", row["developmental stage"]) if stage.strip()}
        invalid = stages - ALLOWED_STAGES
        for stage in sorted(invalid):
            issues.append(f"Row {row_number} ({row['outcome id']}): invalid stage {stage}")

        has_prior_development = bool(stage_history[outcome_id] & {"introduce", "practice"})
        prerequisites, external_prior, invalid_prerequisites = parse_prerequisites(row["outcome prerequisites"])
        for invalid_prerequisite in invalid_prerequisites:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): invalid prerequisite {invalid_prerequisite}"
            )
        if stages & {"master", "assess"} and not has_prior_development and not external_prior:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): mastery/assessment appears before introduction or practice"
            )
        pending_stages[outcome_id].update(stages & ALLOWED_STAGES)

        if stages & {"master", "assess"} and not row["feedback/assessment"]:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): mastery/assessment has no feedback or assessment evidence"
            )

        graph[outcome_id].update(prerequisites)

        status = normalize(row["status"])
        if status and status not in VALID_STATUSES:
            issues.append(f"Row {row_number} ({row['outcome id']}): unknown status {row['status']}")

        workload = parse_positive_finite(row["expected student workload (hours)"])
        if row["expected student workload (hours)"] and workload is None:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): workload must be a positive number"
            )
        if workload is not None:
            workload_by_module[normalize(row["module/week"])] += workload

    for outcome, prerequisites in graph.items():
        for prerequisite in prerequisites:
            if prerequisite not in outcome_ids:
                issues.append(f"{outcome}: unknown prerequisite outcome {prerequisite}")

    for cycle in find_cycles(graph):
        issues.append(f"Circular outcome prerequisites: {cycle}")

    if max_hours is not None:
        for module, hours in sorted(workload_by_module.items()):
            if hours > max_hours:
                issues.append(
                    f"Module/week {module}: workload {hours:g} exceeds limit {max_hours:g}"
                )

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path, args.max_hours_per_module)
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"GAP: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print(f"OK: curriculum sequence and declared-coherence checks passed; manual course review still required: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
