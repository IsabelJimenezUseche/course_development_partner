#!/usr/bin/env python3
"""Validate a connected portable course-development project.

Exit codes:
  0: declared structural and cross-file checks pass
  1: file, parsing, or structural error
  2: project-state, readiness, or consistency gaps detected
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import validate_alignment_map
import validate_artifact_manifest
import validate_assessment_blueprint
import validate_course_curriculum_map
import validate_design_state
from _tabular import (
    load_table,
    local_reference_path,
    normalize,
    normalized_mapping,
    normalized_row,
    parse_identifier_list,
    parse_iso_date,
)


INDEX_REQUIRED = (
    "state file",
    "purpose",
    "authority/owner",
    "schema version",
    "status",
    "last updated",
    "notes",
)
ACTIVE_STATUSES = {"draft", "review", "approved", "blocked"}
INDEX_STATUSES = ACTIVE_STATUSES | {"retired", "not-applicable", "superseded"}
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate indexed state files and cross-file identifiers in a course project.",
        epilog=(
            "Examples:\n"
            "  validate_project.py ./course-project\n"
            "  validate_project.py ./course-project --design-profile handoff --max-hours-per-module 8"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Project directory containing project-index.md")
    parser.add_argument(
        "--design-profile",
        choices=("establish", "produce", "handoff"),
        default="produce",
    )
    parser.add_argument("--max-hours-per-module", type=float)
    parser.add_argument("--allow-formal-validation", action="store_true")
    return parser.parse_args()


def schema_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"^\s*-\s*Schema version:\s*(\S+)\s*$", text, flags=re.I | re.M)
    return match.group(1) if match else ""


def table_identifiers(path: Path, required: tuple[str, ...], field: str) -> tuple[set[str], list[str]]:
    _, headers, rows = load_table(path, required)
    mapping = normalized_mapping(headers, required)
    identifiers: set[str] = set()
    issues: list[str] = []
    for row_number, raw in enumerate(rows, start=1):
        value = normalized_row(raw, mapping)[field]
        if not value:
            continue
        try:
            identifiers.update(parse_identifier_list(value, field_name=field))
        except ValueError as exc:
            issues.append(f"{path.name} row {row_number}: {exc}")
    return identifiers, issues


def validate_index(project: Path) -> tuple[list[str], list[str], dict[str, Path]]:
    index = project / "project-index.md"
    try:
        _, headers, raw_rows = load_table(index, INDEX_REQUIRED)
        mapping = normalized_mapping(headers, INDEX_REQUIRED)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], [], {}

    errors: list[str] = []
    issues: list[str] = []
    active_files: dict[str, Path] = {}
    seen: set[str] = set()
    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        state_file = row["state file"]
        status = normalize(row["status"])
        if not state_file:
            issues.append(f"Project index row {row_number}: missing state file")
            continue
        if state_file in seen:
            issues.append(f"Project index row {row_number}: duplicate state file {state_file}")
        seen.add(state_file)
        if status not in INDEX_STATUSES:
            issues.append(f"Project index row {row_number}: unknown status {row['status']}")
        for field in ("purpose", "authority/owner", "schema version", "status", "last updated"):
            if not row[field]:
                issues.append(f"Project index row {row_number} ({state_file}): missing {field}")
        if row["last updated"] and not parse_iso_date(row["last updated"]):
            issues.append(f"Project index row {row_number} ({state_file}): last updated must use YYYY-MM-DD")

        target = local_reference_path(state_file, project)
        if status in ACTIVE_STATUSES:
            if target is None or not target.is_file():
                issues.append(f"Project index row {row_number}: active state file does not exist: {state_file}")
                continue
            active_files[target.name] = target
            try:
                actual_version = schema_version(target)
            except (OSError, UnicodeError) as exc:
                errors.append(f"Cannot read {state_file}: {exc}")
                continue
            if not actual_version:
                issues.append(f"{state_file}: missing schema version")
            elif actual_version != row["schema version"]:
                issues.append(
                    f"{state_file}: schema version {actual_version} does not match index {row['schema version']}"
                )
        elif status == "not-applicable" and not row["notes"]:
            issues.append(f"Project index row {row_number} ({state_file}): not-applicable requires a rationale")
    return errors, issues, active_files


def validate_project(
    project: Path,
    design_profile: str,
    max_hours: float | None,
    allow_formal_validation: bool,
) -> tuple[list[str], list[str]]:
    if not project.is_dir():
        return [f"Project directory does not exist: {project}"], []
    errors, issues, active = validate_index(project)
    if errors:
        return errors, issues

    component_calls = {
        "course-design-brief.md": lambda path: validate_design_state.validate(path, design_profile),
        "alignment-map.md": validate_alignment_map.validate,
        "artifact-manifest.md": lambda path: validate_artifact_manifest.validate(path, True),
        "assessment-blueprint.md": lambda path: validate_assessment_blueprint.validate(
            path, [], allow_formal_validation, None
        ),
        "course-curriculum-map.md": lambda path: validate_course_curriculum_map.validate(path, max_hours),
    }
    for name, call in component_calls.items():
        path = active.get(name)
        if path is None:
            continue
        component_errors, component_issues = call(path)
        errors.extend(f"{name}: {item}" for item in component_errors)
        issues.extend(f"{name}: {item}" for item in component_issues)

    alignment_path = active.get("alignment-map.md")
    if errors or alignment_path is None:
        return errors, issues

    try:
        alignment_ids, identifier_issues = table_identifiers(
            alignment_path,
            (
                "outcome id", "observable learning outcome", "evidence of learning",
                "learning activity/support", "feedback or assessment", "status"
            ),
            "outcome id",
        )
        issues.extend(identifier_issues)
        cross_files = (
            (
                "assessment-blueprint.md",
                (
                    "item id", "outcome(s)", "intended interpretation/use", "evidence claim",
                    "cognitive demand", "item type", "dependency", "expected time (min)", "points",
                    "construct-irrelevant barriers", "status"
                ),
                "outcome(s)",
            ),
            (
                "course-curriculum-map.md",
                (
                    "sequence", "module/week", "outcome id", "developmental stage",
                    "outcome prerequisites", "learning experience/evidence", "feedback/assessment",
                    "expected student workload (hours)", "status"
                ),
                "outcome id",
            ),
            (
                "artifact-manifest.md",
                validate_artifact_manifest.REQUIRED,
                "outcome(s)",
            ),
        )
        for name, required, field in cross_files:
            path = active.get(name)
            if path is None:
                continue
            identifiers, identifier_issues = table_identifiers(path, required, field)
            issues.extend(identifier_issues)
            for identifier in sorted(identifiers - alignment_ids):
                issues.append(f"{name}: outcome is not defined in alignment-map.md: {identifier}")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(str(exc))
    return errors, issues


def main() -> int:
    args = parse_args()
    errors, issues = validate_project(
        args.path,
        args.design_profile,
        args.max_hours_per_module,
        args.allow_formal_validation,
    )
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"ISSUE: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print(f"OK: indexed structural and cross-file checks passed; manual project review still required: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
