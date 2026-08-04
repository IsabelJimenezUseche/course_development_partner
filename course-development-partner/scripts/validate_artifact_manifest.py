#!/usr/bin/env python3
"""Validate an educational artifact manifest.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: readiness or consistency issues detected
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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


REQUIRED = (
    "artifact id",
    "artifact type",
    "artifact family",
    "variant",
    "required variants",
    "file or reference",
    "audience",
    "outcome(s)",
    "status",
    "validation completed",
    "blockers/open issues",
    "last reviewed",
    "production plan",
    "accessibility review",
    "safety review",
)
VALID_STATUSES = {"draft", "review", "validated", "teaching-ready", "retired"}
EMPTY_ISSUES = {"", "-", "none", "n/a", "na"}
REFERENCE_STATES = {"pending", "not required", "not-required"}
UNAPPROVED_SAFETY_STATES = {
    "blocked",
    "draft",
    "not reviewed",
    "pending",
    "review",
    "unreviewed",
    "unverified",
}
REVIEW_REFERENCE_SUFFIXES = {
    ".doc",
    ".docx",
    ".htm",
    ".html",
    ".md",
    ".odt",
    ".pdf",
    ".rtf",
    ".txt",
}
VALID_ARTIFACT_TYPES = {
    "markdown",
    "document",
    "presentation",
    "spreadsheet",
    "pdf",
    "visual",
    "audio",
    "video",
    "other",
}
RICH_TYPES = {
    "document",
    "presentation",
    "spreadsheet",
    "pdf",
    "visual",
    "audio",
    "video",
}
VALID_VARIANTS = {
    "student",
    "instructor",
    "solution",
    "grader",
    "accessible-alternative",
    "source",
    "distribution",
}
VALIDATION_TOKENS = {
    "technical",
    "alignment",
    "source/reuse",
    "structural",
    "rendered/playback",
    "accessibility",
    "privacy/metadata",
    "reopen",
    "manual",
}
BASE_READY_TOKENS = {"technical", "alignment", "accessibility", "reopen"}
RICH_READY_TOKENS = BASE_READY_TOKENS | {
    "source/reuse",
    "structural",
    "rendered/playback",
    "privacy/metadata",
}


def is_reference_state(value: str) -> bool:
    normalized = normalize(value)
    return (
        normalized in REFERENCE_STATES
        or normalized.startswith("not applicable")
        or normalized.startswith("n/a —")
        or normalized.startswith("n/a -")
    )


def is_safety_not_required(value: str) -> bool:
    normalized = normalize(value)
    if normalized in {"not required", "not-required"}:
        return True
    return bool(re.fullmatch(r"not applicable\s+(?:—|-)\s+\S.*", normalized))


def looks_like_review_reference(value: str) -> bool:
    target = value.strip()
    if re.fullmatch(r"!?\[[^\]]*\]\(.+\)", target):
        return True
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*://\S+", target):
        return True
    return Path(target).suffix.casefold() in REVIEW_REFERENCE_SUFFIXES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required fields and teaching-readiness claims in an artifact manifest.",
        epilog=(
            "Examples:\n"
            "  validate_artifact_manifest.py artifact-manifest.md\n"
            "  validate_artifact_manifest.py artifact-manifest.csv --check-paths"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path", type=Path, help="Path to artifact-manifest.md or a CSV equivalent"
    )
    parser.add_argument(
        "--check-paths",
        action="store_true",
        help="Verify local file references relative to the manifest directory",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def validate(path: Path, check_paths: bool = False) -> tuple[list[str], list[str]]:
    try:
        _, headers, raw_rows = load_table(path, REQUIRED)
        mapping = normalized_mapping(headers, REQUIRED)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []
    if not raw_rows:
        return [], ["Artifact manifest contains no data rows"]

    errors: list[str] = []
    issues: list[str] = []
    seen_ids: set[str] = set()
    active_ids: set[str] = set()
    family_variants: dict[str, set[str]] = {}
    family_requirements: dict[str, set[str]] = {}
    for row_number, raw in enumerate(raw_rows, start=1):
        row = normalized_row(raw, mapping)
        artifact_id = row["artifact id"]
        label = artifact_id or f"row {row_number}"

        if not artifact_id:
            issues.append(f"Row {row_number}: missing artifact ID")
        else:
            normalized_id = normalize(artifact_id)
            try:
                artifact_ids = parse_identifier_list(artifact_id, field_name="artifact")
                if len(artifact_ids) != 1:
                    issues.append(
                        f"Row {row_number}: artifact ID must contain exactly one identifier"
                    )
                else:
                    normalized_id = next(iter(artifact_ids))
            except ValueError as exc:
                issues.append(f"Row {row_number}: {exc}")
            if normalized_id in seen_ids:
                issues.append(f"Row {row_number}: duplicate artifact ID {artifact_id}")
            seen_ids.add(normalized_id)

        for field in (
            "artifact type",
            "file or reference",
            "audience",
            "outcome(s)",
            "status",
        ):
            if not row[field]:
                issues.append(f"{label}: missing {field}")

        artifact_type = normalize(row["artifact type"])
        if artifact_type and artifact_type not in VALID_ARTIFACT_TYPES:
            issues.append(f"{label}: unknown artifact type {row['artifact type']}")

        if row["outcome(s)"]:
            try:
                parse_identifier_list(row["outcome(s)"], field_name="outcome")
            except ValueError as exc:
                issues.append(f"{label}: {exc}")

        status = normalize(row["status"])
        if status and status not in VALID_STATUSES:
            issues.append(f"{label}: unknown status {row['status']}")
        if status != "retired" and artifact_id:
            active_ids.add(normalize(artifact_id))
        validation_tokens = {
            normalize(token)
            for token in re.split(r"[;,]", row["validation completed"])
            if token.strip()
        }
        invalid_validation = validation_tokens - VALIDATION_TOKENS
        for token in sorted(invalid_validation):
            issues.append(f"{label}: unknown validation token {token}")
        if row["last reviewed"] and not parse_iso_date(row["last reviewed"]):
            issues.append(f"{label}: last reviewed must use YYYY-MM-DD")
        if status in {"validated", "teaching-ready"}:
            if (
                not validation_tokens
                or normalize(row["validation completed"]) in EMPTY_ISSUES
            ):
                issues.append(f"{label}: {status} without validation evidence")
            if not row["last reviewed"]:
                issues.append(f"{label}: {status} without last-reviewed date")
            for token in sorted({"technical", "alignment"} - validation_tokens):
                issues.append(f"{label}: {status} missing validation token {token}")
        if status == "teaching-ready":
            if normalize(row["blockers/open issues"]) not in EMPTY_ISSUES:
                issues.append(
                    f"{label}: teaching-ready with unresolved blockers/open issues"
                )
            required_tokens = (
                RICH_READY_TOKENS if artifact_type in RICH_TYPES else BASE_READY_TOKENS
            )
            for token in sorted(required_tokens - validation_tokens):
                issues.append(
                    f"{label}: teaching-ready missing validation token {token}"
                )
            if artifact_type in RICH_TYPES and (
                not row["production plan"] or is_reference_state(row["production plan"])
            ):
                issues.append(
                    f"{label}: teaching-ready rich artifact is missing production plan"
                )
            if not row["accessibility review"] or is_reference_state(
                row["accessibility review"]
            ):
                issues.append(
                    f"{label}: teaching-ready artifact is missing accessibility review"
                )
            # Safety applies only to hazard-bearing work, which the validator cannot detect.
            # Require an affirmative declaration instead: a review reference, or an explicit
            # not-required/not-applicable statement. A blank cell is an undeclared decision.
            safety_review = row["safety review"]
            normalized_safety = normalize(safety_review)
            if not safety_review:
                issues.append(
                    f"{label}: teaching-ready artifact has no safety review declaration; "
                    "reference the review or state not required"
                )
            elif normalized_safety in UNAPPROVED_SAFETY_STATES:
                issues.append(
                    f"{label}: teaching-ready artifact has unapproved safety review state "
                    f"{safety_review}"
                )
            elif not is_safety_not_required(
                safety_review
            ) and not looks_like_review_reference(safety_review):
                issues.append(
                    f"{label}: teaching-ready safety review must be a review reference or an "
                    "explicit not-required declaration"
                )

        if check_paths and status != "retired":
            for field in (
                "file or reference",
                "production plan",
                "accessibility review",
                "safety review",
            ):
                reference = row[field]
                if field != "file or reference" and is_reference_state(reference):
                    continue
                try:
                    target = local_reference_path(reference, path.parent)
                    if target is not None and not target.exists():
                        issues.append(
                            f"{label}: local {field} does not exist: {reference}"
                        )
                except (OSError, RuntimeError) as exc:
                    errors.append(
                        f"{label}: cannot resolve local {field} {reference}: {exc}"
                    )

        family = normalize(row.get("artifact family", ""))
        variant = normalize(row.get("variant", ""))
        requirements = {
            normalize(token)
            for token in re.split(r"[;,/]", row.get("required variants", ""))
            if token.strip()
        }
        if family:
            if status != "retired":
                family_variants.setdefault(family, set())
                family_requirements.setdefault(family, set()).update(requirements)
            if not variant:
                issues.append(
                    f"{label}: artifact family {family} is missing a variant label"
                )
            else:
                if status != "retired":
                    family_variants[family].add(variant)
                if variant not in VALID_VARIANTS:
                    issues.append(f"{label}: unknown variant {row.get('variant', '')}")
                audiences = {
                    normalize(token)
                    for token in re.split(r"[;,]", row["audience"])
                    if token.strip()
                }
                if (
                    variant in {"student", "instructor", "grader"}
                    and variant not in audiences
                ):
                    issues.append(
                        f"{label}: variant {variant} conflicts with audience {row['audience']}"
                    )
        elif variant or requirements:
            issues.append(
                f"{label}: variant or required variants declared without an artifact family"
            )

    for family, requirements in sorted(family_requirements.items()):
        for requirement in sorted(requirements):
            if requirement not in VALID_VARIANTS:
                issues.append(
                    f"Artifact family {family}: unknown required variant {requirement}"
                )
        missing_variants = requirements - family_variants.get(family, set())
        for variant in sorted(missing_variants):
            issues.append(
                f"Artifact family {family}: required {variant} variant is not represented"
            )

    if not active_ids:
        issues.append("Artifact manifest contains no active artifacts")

    return errors, issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path, args.check_paths)
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="ISSUE",
        ok_message=f"manifest readiness rules passed; manual release review still required: {args.path}",
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
