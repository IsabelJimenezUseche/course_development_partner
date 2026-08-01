#!/usr/bin/env python3
"""Validate a Markdown or CSV course curriculum map.

Exit codes:
  0: valid and coherent
  1: file, parsing, or structural error
  2: coherence or workload gaps detected
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED = (
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


def outcome_tokens(value: str) -> set[str]:
    return {normalize(token) for token in re.findall(r"[A-Za-z]+-[A-Za-z0-9_-]+", value)}


def parse_workload(value: str) -> float | None:
    try:
        number = float(value)
        return number if number > 0 else None
    except ValueError:
        return None


def find_cycles(graph: dict[str, set[str]]) -> list[str]:
    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    active: set[str] = set()
    complete: set[str] = set()

    def visit(node: str) -> None:
        if node in complete:
            return
        if node in active:
            start = visiting.index(node)
            cycle = tuple(visiting[start:] + [node])
            cycles.add(cycle)
            return
        active.add(node)
        visiting.append(node)
        for neighbor in graph.get(node, set()):
            visit(neighbor)
        visiting.pop()
        active.remove(node)
        complete.add(node)

    for node in graph:
        visit(node)
    return [" -> ".join(cycle) for cycle in sorted(cycles)]


def validate(path: Path, max_hours: float | None) -> tuple[list[str], list[str]]:
    try:
        headers, raw_rows = load_rows(path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    mapping = {normalize(header): header for header in headers}
    missing = [column for column in REQUIRED if column not in mapping]
    if missing:
        return [f"Missing required column: {column}" for column in missing], []
    if not raw_rows:
        return [], ["Course curriculum map contains no data rows"]

    issues: list[str] = []
    parsed_rows: list[dict[str, str]] = []
    outcome_ids: set[str] = set()
    stage_history: dict[str, set[str]] = defaultdict(set)
    graph: dict[str, set[str]] = defaultdict(set)
    workload_by_module: dict[str, float] = defaultdict(float)

    for row_number, raw in enumerate(raw_rows, start=1):
        row = {key: (raw.get(original) or "").strip() for key, original in mapping.items()}
        parsed_rows.append(row)
        outcome_id = normalize(row["outcome id"])
        if not outcome_id:
            issues.append(f"Row {row_number}: missing outcome ID")
            continue
        outcome_ids.add(outcome_id)

    for row_number, row in enumerate(parsed_rows, start=1):
        outcome_id = normalize(row["outcome id"])
        if not outcome_id:
            continue
        for field_name in REQUIRED:
            if not row[field_name]:
                issues.append(f"Row {row_number} ({row['outcome id']}): missing {field_name}")

        stages = {normalize(stage) for stage in re.split(r"[;,/]", row["developmental stage"]) if stage.strip()}
        invalid = stages - ALLOWED_STAGES
        for stage in sorted(invalid):
            issues.append(f"Row {row_number} ({row['outcome id']}): invalid stage {stage}")

        has_prior_development = bool(stage_history[outcome_id] & {"introduce", "practice"})
        external_prior = "external:" in normalize(row["outcome prerequisites"])
        if stages & {"master", "assess"} and not has_prior_development and not external_prior:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): mastery/assessment appears before introduction or practice"
            )
        stage_history[outcome_id].update(stages & ALLOWED_STAGES)

        if stages & {"master", "assess"} and not row["feedback/assessment"]:
            issues.append(
                f"Row {row_number} ({row['outcome id']}): mastery/assessment has no feedback or assessment evidence"
            )

        prerequisites = outcome_tokens(row["outcome prerequisites"])
        if "external:" not in normalize(row["outcome prerequisites"]):
            graph[outcome_id].update(prerequisites)

        workload = parse_workload(row["expected student workload (hours)"])
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
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
