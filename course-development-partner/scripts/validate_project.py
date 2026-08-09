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
from collections.abc import Callable
from pathlib import Path

import validate_alignment_map
import validate_artifact_manifest
import validate_assessment_blueprint
import validate_course_curriculum_map
import validate_data_task_record
import validate_design_state
import validate_handoff_state
from _tabular import (
    emit_report,
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
VALID_ENGAGEMENT_TIERS = {"project", "course"}
PROFILE_REQUIRED_STATE = {
    "establish": {"course-design-brief.md"},
    "produce": {"course-design-brief.md", "alignment-map.md"},
    "handoff": {
        "course-design-brief.md",
        "alignment-map.md",
        "artifact-manifest.md",
        "design-log.md",
        "source-register.md",
        "capability-manifest.md",
    },
}
TIER_REQUIRED_STATE = {
    "project": set(),
    "course": {"course-curriculum-map.md"},
}


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
    parser.add_argument(
        "path", type=Path, help="Project directory containing project-index.md"
    )
    parser.add_argument(
        "--design-profile",
        choices=("establish", "produce", "handoff"),
        default="produce",
    )
    parser.add_argument("--max-hours-per-module", type=float)
    parser.add_argument("--allow-formal-validation", action="store_true")
    parser.add_argument(
        "--check-practice-distribution",
        action="store_true",
        help=(
            "Report outcomes whose repeated practice is massed in a single module/week "
            "in the course curriculum map"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def schema_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    match = re.search(r"^\s*-\s*Schema version:\s*(\S+)\s*$", text, flags=re.I | re.M)
    return match.group(1) if match else ""


def metadata_value(text: str, label: str) -> str:
    values = metadata_values(text, label)
    return values[0] if values else ""


def metadata_values(text: str, label: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(
            rf"^[ \t]*-[ \t]*{re.escape(label)}:[ \t]*([^\r\n]*)[ \t]*$",
            text,
            flags=re.I | re.M,
        )
    ]


def table_identifiers(
    path: Path,
    required: tuple[str, ...],
    field: str,
    *,
    active_only: bool = False,
) -> tuple[set[str], list[str]]:
    _, headers, rows = load_table(path, required)
    mapping = normalized_mapping(headers, required)
    identifiers: set[str] = set()
    issues: list[str] = []
    for row_number, raw in enumerate(rows, start=1):
        row = normalized_row(raw, mapping)
        if active_only and normalize(row.get("status", "")) == "retired":
            continue
        value = row[field]
        if not value:
            continue
        try:
            identifiers.update(parse_identifier_list(value, field_name=field))
        except ValueError as exc:
            issues.append(f"{path.name} row {row_number}: {exc}")
    return identifiers, issues


def manifest_artifact_ids(path: Path) -> tuple[set[str], set[str]]:
    """Return (active artifact IDs, IDs whose row claims the data-task-fit token)."""
    required = validate_artifact_manifest.REQUIRED
    _, headers, rows = load_table(path, required)
    mapping = normalized_mapping(headers, required)
    active: set[str] = set()
    claimed: set[str] = set()
    for raw in rows:
        row = normalized_row(raw, mapping)
        if normalize(row["status"]) == "retired":
            continue
        try:
            identifiers = parse_identifier_list(row["artifact id"], field_name="artifact")
        except ValueError:
            continue
        active.update(identifiers)
        tokens = {
            normalize(token)
            for token in re.split(r"[;,]", row["validation completed"])
            if token.strip()
        }
        if "data-task-fit" in tokens:
            claimed.update(identifiers)
    return active, claimed


def check_data_task_fit(
    manifest_path: Path | None, record_path: Path | None
) -> tuple[list[str], list[str]]:
    """A fit claim in the manifest must point at a record that can be re-run."""
    if manifest_path is None:
        return [], []
    try:
        active_ids, claimed_ids = manifest_artifact_ids(manifest_path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"artifact-manifest.md: {exc}"], []
    if not claimed_ids and record_path is None:
        return [], []
    if record_path is None:
        return [], [
            f"artifact-manifest.md: {identifier} claims the data-task-fit token but "
            "the project has no active data-task-record.md, so the claim cannot be "
            "re-executed"
            for identifier in sorted(claimed_ids)
        ]
    try:
        recorded_ids = validate_data_task_record.artifact_ids(record_path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"data-task-record.md: {exc}"], []
    issues = [
        f"artifact-manifest.md: {identifier} claims the data-task-fit token but has "
        "no row in data-task-record.md"
        for identifier in sorted(claimed_ids - recorded_ids)
    ]
    issues.extend(
        f"data-task-record.md: artifact is not active in artifact-manifest.md: "
        f"{identifier}"
        for identifier in sorted(recorded_ids - active_ids)
    )
    return [], issues


def validate_index(
    project: Path,
) -> tuple[list[str], list[str], dict[str, Path], str]:
    index = project / "project-index.md"
    try:
        resolved_project = project.resolve()
        resolved_index = index.resolve()
    except (OSError, RuntimeError) as exc:
        return [f"Cannot resolve project-index.md: {exc}"], [], {}, ""
    try:
        resolved_index.relative_to(resolved_project)
    except ValueError:
        return [], ["project-index.md resolves outside the project directory"], {}, ""
    try:
        index_text, headers, raw_rows = load_table(index, INDEX_REQUIRED)
        mapping = normalized_mapping(headers, INDEX_REQUIRED)
        index_version = schema_version(index)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], [], {}, ""

    errors: list[str] = []
    issues: list[str] = []
    active_files: dict[str, Path] = {}
    seen: set[str] = set()
    seen_targets: dict[Path, int] = {}
    engagement_tier = normalize(metadata_value(index_text, "Engagement tier"))
    index_dates = metadata_values(index_text, "Last updated")
    if not index_version:
        issues.append("project-index.md: missing schema version")
    if not index_dates or not index_dates[0]:
        issues.append("project-index.md: missing last-updated date")
    elif len(index_dates) > 1:
        issues.append("project-index.md: duplicate last-updated metadata")
    elif not parse_iso_date(index_dates[0]):
        issues.append("project-index.md: last updated must use YYYY-MM-DD")
    if not engagement_tier:
        issues.append("project-index.md: missing engagement tier")
    elif engagement_tier not in VALID_ENGAGEMENT_TIERS:
        issues.append(
            f"project-index.md: unknown engagement tier "
            f"{metadata_value(index_text, 'Engagement tier')}"
        )
    if not raw_rows:
        issues.append("Project index contains no state-file rows")
    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        state_file = row["state file"]
        status = normalize(row["status"])
        if not state_file:
            issues.append(f"Project index row {row_number}: missing state file")
            continue
        raw_duplicate = state_file in seen
        if raw_duplicate:
            issues.append(
                f"Project index row {row_number}: duplicate state file {state_file}"
            )
        seen.add(state_file)
        if status not in INDEX_STATUSES:
            issues.append(
                f"Project index row {row_number}: unknown status {row['status']}"
            )
        for field in (
            "purpose",
            "authority/owner",
            "schema version",
            "status",
            "last updated",
        ):
            if not row[field]:
                issues.append(
                    f"Project index row {row_number} ({state_file}): missing {field}"
                )
        if row["last updated"] and not parse_iso_date(row["last updated"]):
            issues.append(
                f"Project index row {row_number} ({state_file}): last updated must use YYYY-MM-DD"
            )

        try:
            target = local_reference_path(state_file, project)
            if target is not None:
                target = target.resolve()
        except (OSError, RuntimeError) as exc:
            errors.append(f"Cannot resolve state file {state_file}: {exc}")
            continue
        if target is not None:
            try:
                target.relative_to(resolved_project)
            except ValueError:
                issues.append(
                    f"Project index row {row_number}: state file resolves outside "
                    f"the project directory: {state_file}"
                )
                continue
            previous_row = seen_targets.get(target)
            if previous_row is not None:
                if not raw_duplicate:
                    issues.append(
                        f"Project index row {row_number}: state file resolves to the same "
                        f"target as row {previous_row}: {state_file}"
                    )
                continue
            seen_targets[target] = row_number
        if status in ACTIVE_STATUSES:
            if target is None or not target.is_file():
                issues.append(
                    f"Project index row {row_number}: active state file does not exist: {state_file}"
                )
                continue
            if target.name in active_files and active_files[target.name] != target:
                issues.append(
                    f"Project index row {row_number}: duplicate active basename {target.name}"
                )
            active_files[target.name] = target
            try:
                target_text = target.read_text(encoding="utf-8-sig")
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
            if index_version and actual_version and actual_version != index_version:
                issues.append(
                    f"{state_file}: schema version {actual_version} does not match "
                    f"project-index.md development schema {index_version}"
                )
            state_dates = metadata_values(target_text, "Last updated")
            if not state_dates or not state_dates[0]:
                issues.append(f"{state_file}: missing last-updated date")
            elif len(state_dates) > 1:
                issues.append(f"{state_file}: duplicate last-updated metadata")
            elif not parse_iso_date(state_dates[0]):
                issues.append(f"{state_file}: last updated must use YYYY-MM-DD")
            elif state_dates[0] != row["last updated"]:
                issues.append(
                    f"{state_file}: last updated {state_dates[0]} does not match index "
                    f"{row['last updated']}"
                )
        elif status == "not-applicable" and not row["notes"]:
            issues.append(
                f"Project index row {row_number} ({state_file}): not-applicable requires a rationale"
            )
    return errors, issues, active_files, engagement_tier


def validate_project(
    project: Path,
    design_profile: str,
    max_hours: float | None,
    allow_formal_validation: bool,
    check_practice_distribution: bool = False,
) -> tuple[list[str], list[str]]:
    if not project.is_dir():
        return [f"Project directory does not exist: {project}"], []
    errors, issues, active, engagement_tier = validate_index(project)
    if errors:
        return errors, issues

    for name in sorted(PROFILE_REQUIRED_STATE[design_profile] - set(active)):
        issues.append(
            f"{design_profile} profile requires an active project-index entry for {name}"
        )

    if engagement_tier in TIER_REQUIRED_STATE and design_profile in {
        "produce",
        "handoff",
    }:
        for name in sorted(TIER_REQUIRED_STATE[engagement_tier] - set(active)):
            issues.append(
                f"{engagement_tier} engagement tier with {design_profile} profile requires "
                f"an active project-index entry for {name}"
            )

    brief_path = active.get("course-design-brief.md")
    if brief_path is not None:
        try:
            brief_tier = normalize(
                metadata_value(
                    brief_path.read_text(encoding="utf-8-sig"), "Engagement tier"
                )
            )
            if engagement_tier and brief_tier and engagement_tier != brief_tier:
                issues.append(
                    "course-design-brief.md engagement tier does not match "
                    f"project-index.md: {brief_tier} != {engagement_tier}"
                )
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read course-design-brief.md engagement tier: {exc}")

    alignment_path = active.get("alignment-map.md")

    component_calls: dict[str, Callable[[Path], tuple[list[str], list[str]]]] = {
        "course-design-brief.md": lambda path: validate_design_state.validate(
            path, design_profile
        ),
        "alignment-map.md": validate_alignment_map.validate,
        "artifact-manifest.md": lambda path: validate_artifact_manifest.validate(
            path, True
        ),
        "assessment-blueprint.md": lambda path: validate_assessment_blueprint.validate(
            path, [], allow_formal_validation, alignment_path
        ),
        "data-task-record.md": validate_data_task_record.validate,
        "design-log.md": lambda path: validate_handoff_state.validate(
            path, "design-log", design_profile == "handoff"
        ),
        "source-register.md": lambda path: validate_handoff_state.validate(
            path, "source-register", design_profile == "handoff"
        ),
        "capability-manifest.md": lambda path: validate_handoff_state.validate(
            path, "capability-manifest", design_profile == "handoff"
        ),
        "course-curriculum-map.md": lambda path: validate_course_curriculum_map.validate(
            path,
            max_hours,
            design_profile == "handoff",
            check_practice_distribution,
        ),
    }
    for name, call in component_calls.items():
        path = active.get(name)
        if path is None:
            continue
        component_errors, component_issues = call(path)
        errors.extend(f"{name}: {item}" for item in component_errors)
        issues.extend(f"{name}: {item}" for item in component_issues)

    fit_errors, fit_issues = check_data_task_fit(
        active.get("artifact-manifest.md"), active.get("data-task-record.md")
    )
    errors.extend(fit_errors)
    issues.extend(fit_issues)

    if errors or alignment_path is None:
        return errors, issues

    try:
        alignment_ids, identifier_issues = table_identifiers(
            alignment_path,
            (
                "outcome id",
                "observable learning outcome",
                "cognitive demand",
                "evidence of learning",
                "learning mechanism",
                "learning activity/support",
                "feedback or assessment",
                "status",
            ),
            "outcome id",
            active_only=True,
        )
        issues.extend(identifier_issues)
        cross_files = (
            (
                "assessment-blueprint.md",
                (
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
                ),
                "outcome(s)",
            ),
            (
                "course-curriculum-map.md",
                (
                    "sequence",
                    "module/week",
                    "outcome id",
                    "developmental stage",
                    "outcome prerequisites",
                    "learning experience/evidence",
                    "feedback/assessment",
                    "expected student workload (hours)",
                    "status",
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
            identifiers, identifier_issues = table_identifiers(
                path,
                required,
                field,
                active_only=True,
            )
            issues.extend(identifier_issues)
            for identifier in sorted(identifiers - alignment_ids):
                issues.append(
                    f"{name}: outcome is not defined in alignment-map.md: {identifier}"
                )
            if name == "course-curriculum-map.md" and engagement_tier == "course":
                for identifier in sorted(alignment_ids - identifiers):
                    issues.append(
                        "course-curriculum-map.md: active aligned outcome is not mapped "
                        f"for the Course tier: {identifier}"
                    )
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
        args.check_practice_distribution,
    )
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="ISSUE",
        ok_message=f"indexed structural and cross-file checks passed; manual project review still required: {args.path}",
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
