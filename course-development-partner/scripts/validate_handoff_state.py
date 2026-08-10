#!/usr/bin/env python3
"""Validate the design log, source register, and capability manifest.

The handoff profile requires these three files, but requiring a file is not the
same as requiring content: a template copied and never filled in satisfies an
existence check while carrying no provenance, no decision history, and no tool
record. These are lightweight structural checks that a handoff bundle actually
says something.

Exit codes:
  0: the file carries usable content for its kind
  1: file, parsing, or structural error
  2: completeness gaps detected
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _tabular import (
    emit_report,
    load_table,
    normalize,
    normalized_mapping,
    normalized_row,
    parse_identifier_list,
    parse_iso_date,
)

DESIGN_LOG_REQUIRED = (
    "date",
    "decision or change",
    "rationale",
    "source or owner",
    "affected artifacts",
    "follow-up",
)
SOURCE_REGISTER_REQUIRED = (
    "source id",
    "title",
    "owner/publisher",
    "stable reference",
    "authority type",
    "publication/revision date",
    "last verified",
    "supported claim or artifact",
    "population/context and fit",
    "strength/limits",
    "license/reuse",
    "status",
)
CAPABILITY_REQUIRED = (
    "capability",
    "available provider or tool",
    "access level",
    "intended use",
    "approval required",
    "fallback",
    "verification date",
)

SOURCE_STATUSES = {"draft", "verified", "conflicting", "superseded", "retired"}
AUTHORITY_TYPES = {
    "supplied",
    "institutional",
    "disciplinary",
    "scholarly",
    "external",
    "illustrative",
}
ACCESS_LEVELS = {
    "read",
    "local",
    "draft write",
    "live write",
    "publish",
    "message",
    "grade",
    "permissions",
}
# Values that look filled in but assert nothing.
PLACEHOLDERS = {"", "-", "tbd", "todo", "n/a", "na", "none", "?"}

KINDS = ("design-log", "source-register", "capability-manifest")

# A row that records a missing source is an absence claim, and an absence claim
# nobody can audit is worth little: "we searched and found nothing" and "we
# never looked" read identically afterwards and call for opposite responses.
ABSENCE_CLAIM = re.compile(
    r"\b(?:no (?:source|sources|evidence|literature|reference|study|studies|data)"
    r"|none (?:found|located|available|identified)|not found|nothing found|"
    r"no published|unavailable in the literature|evidence gap|source gap|"
    r"literature gap)\b",
    re.IGNORECASE,
)
# What makes it auditable: the queries behind it.
SEARCH_EVIDENCE = re.compile(
    r"\b(?:search(?:ed|es)?|quer(?:y|ies|ied)|look(?:ed|up)|catalog(?:ue)?s?|"
    r"database|index|scopus|pubmed|eric|ieee|acm|google scholar|web of science|"
    r"library|terms?|keywords?)\b",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that a design log, source register, or capability manifest "
            "carries usable content rather than an unfilled template."
        ),
        epilog=(
            "Examples:\n"
            "  validate_handoff_state.py design-log.md --kind design-log\n"
            "  validate_handoff_state.py source-register.md --kind source-register"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to the state file")
    parser.add_argument(
        "--kind",
        choices=KINDS,
        help="File kind; inferred from the filename when omitted",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Apply handoff-level completeness: full source provenance and "
            "capability use/approval rules"
        ),
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
    return normalize(value) in PLACEHOLDERS


def populated_rows(
    rows: list[dict[str, str]], mapping: dict[str, str], required: tuple[str, ...]
) -> list[tuple[int, dict[str, str]]]:
    """Return (row number, row) for rows carrying any non-placeholder value."""
    result = []
    for number, raw in enumerate(rows, start=1):
        row = normalized_row(raw, mapping)
        if any(not is_placeholder(row[field]) for field in required):
            result.append((number, row))
    return result


def validate_design_log(rows, mapping, strict: bool = False) -> list[str]:
    issues: list[str] = []
    filled = populated_rows(rows, mapping, DESIGN_LOG_REQUIRED)
    if not filled:
        issues.append(
            "Design log records no decisions; a handoff needs the decision history"
        )
    for number, row in filled:
        for field in ("date", "decision or change", "rationale", "source or owner"):
            if is_placeholder(row[field]):
                issues.append(f"Row {number}: missing {field}")
        if row["date"] and not is_placeholder(row["date"]):
            if not parse_iso_date(row["date"]):
                issues.append(f"Row {number}: date must use YYYY-MM-DD")
        claim = f"{row['decision or change']} {row['rationale']}"
        if ABSENCE_CLAIM.search(claim) and not SEARCH_EVIDENCE.search(claim):
            issues.append(
                f"Row {number}: records a missing source without the searches that "
                "justify it; name the catalogues or databases queried and the terms "
                "used, so the absence can be told apart from an unasked question"
            )
    return issues


def validate_source_register(rows, mapping, strict: bool = False) -> list[str]:
    issues: list[str] = []
    filled = populated_rows(rows, mapping, SOURCE_REGISTER_REQUIRED)
    if not filled:
        issues.append(
            "Source register records no sources; a handoff needs claim provenance"
        )
    seen: set[str] = set()
    for number, row in filled:
        identifier = row["source id"]
        if is_placeholder(identifier):
            issues.append(f"Row {number}: missing source ID")
        else:
            try:
                ids = parse_identifier_list(identifier, field_name="source")
                if len(ids) != 1:
                    issues.append(
                        f"Row {number}: source ID must contain exactly one identifier"
                    )
                else:
                    key = next(iter(ids))
                    if key in seen:
                        issues.append(f"Row {number}: duplicate source ID {identifier}")
                    seen.add(key)
            except ValueError as exc:
                issues.append(f"Row {number}: {exc}")
        core = ("title", "authority type", "supported claim or artifact", "status")
        # A source that cannot be located, dated, or reused is not provenance;
        # at handoff the receiving reader has only what this row records.
        handoff_only = (
            "owner/publisher",
            "stable reference",
            "last verified",
            "population/context and fit",
            "strength/limits",
            "license/reuse",
        )
        for field in core + (handoff_only if strict else ()):
            if is_placeholder(row[field]):
                issues.append(f"Row {number}: missing {field}")
        status = normalize(row["status"])
        if status and status not in SOURCE_STATUSES and not is_placeholder(status):
            issues.append(f"Row {number}: unknown status {row['status']}")
        authority = normalize(row["authority type"])
        if authority and "/" in authority:
            issues.append(
                f"Row {number}: authority type still lists every option; choose one of "
                f"{', '.join(sorted(AUTHORITY_TYPES))}"
            )
        elif authority and authority not in AUTHORITY_TYPES and not is_placeholder(authority):
            issues.append(f"Row {number}: unknown authority type {row['authority type']}")
        for field in ("publication/revision date", "last verified"):
            value = row[field]
            if not is_placeholder(value) and not parse_iso_date(value):
                issues.append(f"Row {number}: {field} must use YYYY-MM-DD")
    return issues


def validate_capability_manifest(rows, mapping, strict: bool = False) -> list[str]:
    issues: list[str] = []
    filled = populated_rows(rows, mapping, CAPABILITY_REQUIRED)
    if not filled:
        issues.append(
            "Capability manifest records no capabilities; a handoff needs the tool "
            "and fallback record"
        )
    resolved = 0
    for number, row in filled:
        if is_placeholder(row["capability"]):
            issues.append(f"Row {number}: missing capability")
        access = normalize(row["access level"])
        if access and not is_placeholder(access) and access not in ACCESS_LEVELS:
            issues.append(f"Row {number}: unknown access level {row['access level']}")
        for field in ("intended use", "approval required") if strict else ():
            if is_placeholder(row[field]):
                issues.append(f"Row {number}: missing {field}")
        if is_placeholder(row["fallback"]):
            issues.append(
                f"Row {number}: missing fallback; a capability with no fallback "
                "cannot survive an unavailable tool"
            )
        provider_known = not is_placeholder(row["available provider or tool"])
        if provider_known:
            resolved += 1
            if is_placeholder(row["verification date"]):
                issues.append(
                    f"Row {number}: provider recorded without a verification date"
                )
            elif not parse_iso_date(row["verification date"]):
                issues.append(f"Row {number}: verification date must use YYYY-MM-DD")
    if filled and resolved == 0:
        issues.append(
            "No capability records an available provider or tool; the manifest has "
            "not been resolved against the current client"
        )
    return issues


VALIDATORS = {
    "design-log": (DESIGN_LOG_REQUIRED, validate_design_log),
    "source-register": (SOURCE_REGISTER_REQUIRED, validate_source_register),
    "capability-manifest": (CAPABILITY_REQUIRED, validate_capability_manifest),
}


def validate(
    path: Path, kind: str | None = None, strict: bool = False
) -> tuple[list[str], list[str]]:
    resolved_kind = kind or infer_kind(path)
    if resolved_kind is None:
        return [
            f"Cannot infer state-file kind from {path.name}; pass --kind"
        ], []
    required, checker = VALIDATORS[resolved_kind]
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [str(exc)], []
    # A file with no table at all is an unfilled handoff record, not a corrupt
    # one: report it as the completeness gap it is rather than a parse error.
    if not any(line.lstrip().startswith("|") for line in text.splitlines()):
        return [], [f"{resolved_kind} has no records table; the handoff record is empty"]
    try:
        _, headers, rows = load_table(path, required)
        mapping = normalized_mapping(headers, required)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []
    return [], checker(rows, mapping, strict)


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path, args.kind, args.strict)
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="GAP",
        ok_message="state file carries usable content; manual review still required",
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
