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
import validate_release_record
from _tabular import (
    emit_report,
    load_table,
    local_reference_path,
    metadata_value,
    metadata_values,
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
# Every recognized portable-state filename. The state contract requires each
# active one to appear in the project index; without this list the validator
# only ever sees the files it was already told about, so omitting a record from
# the index is a way to skip its checks entirely.
RECOGNIZED_STATE = frozenset(
    {
        "accessibility-review.md",
        "alignment-map.md",
        "artifact-manifest.md",
        "assessment-blueprint.md",
        "capability-manifest.md",
        "context-brief.md",
        "course-curriculum-map.md",
        "course-design-brief.md",
        "data-task-record.md",
        "design-log.md",
        "implementation-evidence-plan.md",
        "implementation-plan.md",
        "lesson-storyboard.md",
        "production-plan.md",
        "safety-review.md",
        "source-register.md",
    }
)
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


def manifest_artifact_ids(path: Path) -> tuple[set[str], dict[str, str]]:
    """Return active artifact IDs and, per claiming ID, its evidence reference."""
    required = validate_artifact_manifest.REQUIRED
    _, headers, rows = load_table(path, required)
    mapping = normalized_mapping(headers, required)
    active: set[str] = set()
    claimed: dict[str, str] = {}
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
            for identifier in identifiers:
                claimed[identifier] = row["data-task-fit evidence"]
    return active, claimed


def check_data_task_fit(
    manifest_path: Path | None, record_path: Path | None
) -> tuple[list[str], list[str]]:
    """A fit claim in the manifest must point at the record that rechecks it."""
    if manifest_path is None:
        return [], []
    try:
        active_ids, claimed = manifest_artifact_ids(manifest_path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"artifact-manifest.md: {exc}"], []
    if not claimed and record_path is None:
        return [], []
    if record_path is None:
        return [], [
            f"artifact-manifest.md: {identifier} claims the data-task-fit token but "
            "the project has no active data-task-record.md, so the claim cannot be "
            "rechecked"
            for identifier in sorted(claimed)
        ]
    try:
        recorded_ids = validate_data_task_record.artifact_ids(record_path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"data-task-record.md: {exc}"], []
    issues = [
        f"artifact-manifest.md: {identifier} claims the data-task-fit token but has "
        "no row in data-task-record.md"
        for identifier in sorted(set(claimed) - recorded_ids)
    ]
    # Matching artifact IDs is not the same as pointing at the record. Without
    # this, any Markdown reference satisfies the evidence cell as long as some
    # record elsewhere happens to carry the same ID.
    for identifier, evidence in sorted(claimed.items()):
        if identifier not in recorded_ids:
            continue
        try:
            target = local_reference_path(evidence, manifest_path.parent)
        except (OSError, RuntimeError) as exc:
            issues.append(
                f"artifact-manifest.md: {identifier} data-task-fit evidence cannot be "
                f"resolved: {exc}"
            )
            continue
        if target is None or target.resolve() != record_path.resolve():
            issues.append(
                f"artifact-manifest.md: {identifier} data-task-fit evidence points to "
                f"{evidence or 'nothing'} rather than the active data-task-record.md "
                "that rechecks the claim"
            )
    issues.extend(
        f"data-task-record.md: artifact is not active in artifact-manifest.md: "
        f"{identifier}"
        for identifier in sorted(recorded_ids - active_ids)
    )
    return [], issues


def check_unindexed_state(project: Path, indexed: dict[str, Path]) -> list[str]:
    """Report recognized state files present in the project but absent from the index.

    Validation reaches a file through the index, so an unindexed record is an
    unchecked one: a model can write an assessment blueprint or a safety review,
    leave it out of the index, and skip every rule that would have applied to it.
    """
    issues: list[str] = []
    known = {path.resolve() for path in indexed.values()}
    for candidate in sorted(project.rglob("*.md")):
        if candidate.name not in RECOGNIZED_STATE:
            continue
        try:
            if candidate.resolve() in known:
                continue
        except (OSError, RuntimeError):
            continue
        issues.append(
            f"{candidate.relative_to(project)} is a portable-state file that no "
            "active project-index row lists; index it or mark it not-applicable "
            "with a rationale"
        )
    return issues


def check_referenced_release_records(
    project: Path, manifest_path: Path
) -> tuple[list[str], list[str]]:
    """Validate the records a teaching-ready row cites as its release evidence.

    The manifest can only check that a reference looks like a file and that the
    file exists. Neither says anything was reviewed, so a blank copied template
    supported teaching-ready status until this ran.
    """
    required = validate_artifact_manifest.REQUIRED
    try:
        _, headers, rows = load_table(manifest_path, required)
        mapping = normalized_mapping(headers, required)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"artifact-manifest.md: {exc}"], []

    kinds = {
        "safety review": "safety-review",
        "accessibility review": "accessibility-review",
        "production plan": "production-plan",
    }
    issues: list[str] = []
    seen: set[tuple[Path, str]] = set()
    for raw in rows:
        row = normalized_row(raw, mapping)
        if normalize(row["status"]) != "teaching-ready":
            continue
        label = row["artifact id"] or "row"
        for column, kind in kinds.items():
            reference = row[column]
            if not reference or validate_artifact_manifest.is_reference_state(reference):
                continue
            if validate_artifact_manifest.is_not_applicable(reference):
                continue
            try:
                target = local_reference_path(reference, manifest_path.parent)
            except (OSError, RuntimeError) as exc:
                issues.append(f"{label}: cannot resolve {column}: {exc}")
                continue
            if target is None or target.suffix.casefold() != ".md":
                # A PDF or a URL may well be the authoritative review, but a
                # filename is not an approval. The project needs a record here
                # that cites it and carries the decision.
                issues.append(
                    f"{label}: {column} {reference} cannot be checked; a "
                    f"teaching-ready row needs a local {kind}.md recording the "
                    "decision, which may cite the external document"
                )
                continue
            if not target.is_file():
                continue
            key = (target.resolve(), kind)
            if key in seen:
                continue
            seen.add(key)
            record_errors, record_issues = validate_release_record.validate(target, kind)
            issues.extend(f"{label}: {item}" for item in record_errors + record_issues)
    return [], issues


def check_planned_capability(
    manifest_path: Path | None, capability_path: Path | None
) -> tuple[list[str], list[str]]:
    """Every planned artifact type must appear in the capability manifest.

    A real run planned a design-project brief and a spreadsheet calculator that
    the host could not produce. The capability manifest existed and was filled
    in; nothing required consulting it before naming artifacts, so the brief
    kept listing deliverables that were never coming.

    Absence is the finding, not unavailability: a capability recorded as
    unavailable carries a fallback, which is the honest path. A capability that
    was never recorded means nobody checked.
    """
    if manifest_path is None or capability_path is None:
        return [], []
    required = validate_artifact_manifest.REQUIRED
    try:
        _, headers, rows = load_table(manifest_path, required)
        mapping = normalized_mapping(headers, required)
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"artifact-manifest.md: {exc}"], []
    try:
        _, cap_headers, cap_rows = load_table(
            capability_path, validate_handoff_state.CAPABILITY_REQUIRED
        )
        cap_mapping = normalized_mapping(
            cap_headers, validate_handoff_state.CAPABILITY_REQUIRED
        )
    except (OSError, UnicodeError, ValueError):
        # An unreadable or unfilled capability manifest is already reported by
        # validate_handoff_state as the gap it is; do not restate it as an error.
        return [], []

    declared = " ".join(
        normalize(normalized_row(raw, cap_mapping)["capability"]) for raw in cap_rows
    )
    issues: list[str] = []
    reported: set[str] = set()
    for raw in rows:
        row = normalized_row(raw, mapping)
        if normalize(row["status"]) == "retired":
            continue
        artifact_type = normalize(row["artifact type"])
        if artifact_type not in validate_artifact_manifest.RICH_TYPES:
            continue
        if artifact_type in declared or artifact_type in reported:
            continue
        reported.add(artifact_type)
        issues.append(
            f"artifact-manifest.md: {artifact_type} artifacts are planned but "
            "capability-manifest.md records no capability for them; record the "
            "provider and fallback, or mark the artifact owner-supplied"
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
        "data-task-record.md": lambda path: validate_data_task_record.validate(
            path, project
        ),
        "safety-review.md": lambda path: validate_release_record.validate(
            path, "safety-review"
        ),
        "accessibility-review.md": lambda path: validate_release_record.validate(
            path, "accessibility-review"
        ),
        "production-plan.md": lambda path: validate_release_record.validate(
            path, "production-plan"
        ),
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

    issues.extend(check_unindexed_state(project, active))

    capability_errors, capability_issues = check_planned_capability(
        active.get("artifact-manifest.md"), active.get("capability-manifest.md")
    )
    errors.extend(capability_errors)
    issues.extend(capability_issues)

    manifest_path = active.get("artifact-manifest.md")
    if manifest_path is not None:
        release_errors, release_issues = check_referenced_release_records(
            project, manifest_path
        )
        errors.extend(release_errors)
        issues.extend(release_issues)

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
