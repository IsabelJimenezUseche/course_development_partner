#!/usr/bin/env python3
"""Validate the safety review, accessibility review, and production plan.

The artifact manifest checks that these records are *referenced* and that the
file exists. That is not the same as checking that anything was reviewed: a
template copied into the project and never filled in satisfies both, so a blank
safety review could support teaching-ready status for hazard-bearing work.

This validator reads the record and asks whether it carries a decision. The
three kinds share one script because they share one purpose — each is the
evidence behind a release claim, and each fails the same way.

What it cannot do: judge whether the review was competent, or whether the named
owner was qualified to approve. It checks that a responsible person is named,
that the governing source and dates are present, and that the release decision
is affirmative and unblocked. The judgment stays with the responsible owner.

Exit codes:
  0: the record carries an affirmative, unblocked release decision
  1: file, parsing, or structural error
  2: completeness gaps detected
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _tabular import (
    emit_report,
    metadata_values,
    normalize,
    parse_iso_date,
)

KINDS = ("safety-review", "accessibility-review", "production-plan")

# Values that look filled in but assert nothing.
PLACEHOLDERS = {"", "-", "tbd", "todo", "n/a", "na", "none", "?", "pending"}
# Bracketed prompt text left in place from the template.
AFFIRMATIVE = {"yes", "y", "true", "approved", "complete", "completed"}
NEGATIVE = {"no", "n", "false", "blocked", "not approved", "denied"}
CLEAR = {"none", "none identified", "no", "n/a", "na", "-", "none known"}

SAFETY_REQUIRED = (
    "Responsible safety owner and role",
    "Governing document, version, and date",
    "Activity, session, or artifact(s) covered",
)
SAFETY_DATES = ("Source last verified", "Approval date")
ACCESSIBILITY_REQUIRED = (
    "Required technical target",
    "Artifact(s), pages, states, and user paths reviewed",
    "Reviewers and qualifications",
    "Claim supported by this review",
    "Claims not supported",
)
ACCESSIBILITY_DATES = ("Source last verified", "Review date")
PRODUCTION_REQUIRED = (
    "Artifact ID and working title",
    "Requested final format",
    "Production method",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that a safety review, accessibility review, or production "
            "plan records a decision rather than an unfilled template."
        ),
        epilog=(
            "Examples:\n"
            "  validate_release_record.py safety-review.md\n"
            "  validate_release_record.py plan.md --kind production-plan"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to the release record")
    parser.add_argument(
        "--kind", choices=KINDS, help="Record kind; inferred from the filename when omitted"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def infer_kind(path: Path) -> str | None:
    stem = normalize(path.stem)
    for kind in KINDS:
        if stem == kind:
            return kind
    return None


def is_placeholder(value: str) -> bool:
    stripped = value.strip()
    if normalize(stripped) in PLACEHOLDERS:
        return True
    # `- Field: [instructor of record, laboratory manager]` is the prompt, not
    # an answer; so is a bare list of the options the template offers.
    if stripped.startswith("[") and stripped.endswith("]"):
        return True
    return bool(stripped) and set(stripped) <= set("| ")


def field(text: str, label: str) -> str:
    values = metadata_values(text, label)
    return values[0] if values else ""


def require_fields(text: str, labels: tuple[str, ...]) -> list[str]:
    return [
        f"missing {label.lower()}"
        for label in labels
        if is_placeholder(field(text, label))
    ]


def require_dates(text: str, labels: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for label in labels:
        value = field(text, label)
        if is_placeholder(value):
            issues.append(f"missing {label.lower()}")
        elif not parse_iso_date(value):
            issues.append(f"{label.lower()} must use YYYY-MM-DD")
    return issues


def is_clear(value: str) -> bool:
    """An 'unresolved blockers' field that genuinely records none."""
    return normalize(value) in CLEAR


def is_blank(value: str) -> bool:
    """Unfilled, judged without treating "none" as unfilled.

    `none` is the right answer to "unresolved blockers" and the wrong answer to
    "responsible safety owner", so those two questions cannot share one test.
    """
    stripped = value.strip()
    if not stripped:
        return True
    if stripped.startswith("[") and stripped.endswith("]"):
        return True
    return normalize(stripped) in {"-", "tbd", "todo", "?", "pending"}


def validate_safety(text: str) -> list[str]:
    issues = require_fields(text, SAFETY_REQUIRED)
    issues.extend(require_dates(text, SAFETY_DATES))

    blockers = field(text, "Unresolved blockers")
    if is_blank(blockers):
        issues.append(
            "unresolved blockers is blank; state none explicitly or list them"
        )
    elif not is_clear(blockers):
        issues.append(f"unresolved safety blocker recorded: {blockers}")

    for label in ("Responsible owner approval recorded", "Approved for student use"):
        value = normalize(field(text, label))
        # The template ships "yes | no"; leaving both is not a decision.
        if is_placeholder(value) or "|" in value:
            issues.append(f"{label.lower()} is undecided")
        elif value in NEGATIVE:
            issues.append(f"{label.lower()} is {value}; release is blocked")
        elif value not in AFFIRMATIVE:
            issues.append(f"unrecognized value for {label.lower()}: {value}")
    return issues


def validate_accessibility(text: str) -> list[str]:
    issues = require_fields(text, ACCESSIBILITY_REQUIRED)
    issues.extend(require_dates(text, ACCESSIBILITY_DATES))

    untested = field(text, "Untested content, criteria, technologies, states, or user paths")
    if is_placeholder(untested):
        issues.append(
            "untested scope is blank; an accessibility claim must state what it "
            "does not cover"
        )
    barriers = field(text, "Unresolved barriers")
    if is_blank(barriers):
        issues.append("unresolved barriers is blank; state none explicitly or list them")
    elif not is_clear(barriers):
        issues.append(f"unresolved accessibility barrier recorded: {barriers}")
    return issues


def validate_production(text: str) -> list[str]:
    issues = require_fields(text, PRODUCTION_REQUIRED)

    blockers = field(text, "Blockers")
    if is_blank(blockers):
        issues.append("blockers is blank; state none explicitly or list them")
    elif not is_clear(blockers):
        issues.append(f"unresolved production blocker recorded: {blockers}")

    status = normalize(field(text, "Final status"))
    if is_placeholder(status) or "|" in status:
        issues.append("final status is undecided")
    elif status == "blocked":
        issues.append("final status is blocked; release is blocked")
    elif status != "teaching-ready":
        issues.append(
            f"final status is {status}; a manifest row citing this plan as "
            "teaching-ready needs teaching-ready here"
        )

    updated = normalize(field(text, "Artifact-manifest entry updated"))
    if is_placeholder(updated) or "|" in updated:
        issues.append("artifact-manifest entry updated is undecided")
    elif updated in NEGATIVE:
        issues.append("artifact-manifest entry has not been updated from this plan")
    return issues


VALIDATORS = {
    "safety-review": validate_safety,
    "accessibility-review": validate_accessibility,
    "production-plan": validate_production,
}


def validate(path: Path, kind: str | None = None) -> tuple[list[str], list[str]]:
    resolved_kind = kind or infer_kind(path)
    if resolved_kind is None:
        return [f"Cannot infer record kind from {path.name}; pass --kind"], []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [str(exc)], []

    issues: list[str] = []
    versions = metadata_values(text, "Schema version")
    if not versions or is_placeholder(versions[0]):
        issues.append("missing schema version")
    updated = metadata_values(text, "Last updated")
    if not updated or is_placeholder(updated[0]):
        issues.append("missing last-updated date")
    elif not parse_iso_date(updated[0]):
        issues.append("last updated must use YYYY-MM-DD")

    issues.extend(VALIDATORS[resolved_kind](text))
    return [], [f"{resolved_kind}: {issue}" for issue in issues]


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path, args.kind)
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="GAP",
        ok_message=(
            "release record carries an affirmative, unblocked decision; whether "
            "the review itself was adequate still requires a qualified human"
        ),
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
