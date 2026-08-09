#!/usr/bin/env python3
"""Revalidate the structural fit claims recorded in a data-task record.

A validation token in the artifact manifest is a claim that somebody executed
the requested operation on the exact supplied dataset. On its own it is
self-attested: nothing distinguishes a row where the work happened from a row
where the token was typed. This validator narrows that gap by rechecking each
recorded claim against the dataset it names.

What it proves, precisely:

* the dataset named in the row is present and unchanged since the check was
  recorded, by comparing its SHA-256 against the recorded hash;
* the columns the row names exist, and their types, roles, levels, pairing, and
  observation counts support the declared representation.

What it does not prove: that the recorded ``Result`` is correct. It does not
redraw the chart or recompute the statistic, so a recorded slope, mean, or
interpretation is checked by a human or not at all. The hash is what stands
between those two: a dataset whose values changed while its schema held still
fails here, which is the case a structural check alone cannot see.

A row that cannot be rechecked — an absent dataset, an unknown representation,
unparseable roles — is reported as a gap, because an unverifiable claim and a
false one are indistinguishable to the reader.

Exit codes:
  0: every recorded claim rechecks against an unchanged dataset
  1: file, parsing, or structural error
  2: fit-record gaps detected
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import validate_dataset
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
    "dataset file",
    "dataset sha-256",
    "dataset version or date",
    "worksheet",
    "representation",
    "column roles",
    "expected student output",
    "intended interpretation",
    "execution method",
    "execution evidence",
    "executed on",
    "result",
)

EXECUTION_METHODS = {"validator", "code", "manual"}
WORKBOOK_SUFFIXES = {".xlsx", ".xlsm"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
# Values that look filled in but assert nothing.
PLACEHOLDERS = {"", "-", "tbd", "todo", "n/a", "na", "none", "?", "pending"}
# Fields every filled row must carry. Worksheet and execution evidence are
# conditional, so they are checked against the row's own dataset and method.
ALWAYS_REQUIRED = (
    "dataset version or date",
    "expected student output",
    "intended interpretation",
    "result",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recheck each recorded data-task fit claim against the dataset it "
            "names, and confirm that dataset has not changed since."
        ),
        epilog=(
            "Examples:\n"
            "  validate_data_task_record.py data-task-record.md\n"
            "  validate_data_task_record.py data-task-record.md --json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", type=Path, help="Path to data-task-record.md")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def is_placeholder(value: str) -> bool:
    return normalize(value) in PLACEHOLDERS


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_roles(value: str) -> tuple[dict[str, str], list[str]]:
    """Parse `x=mass_kg; y=extension_mm` into role/column pairs."""
    roles: dict[str, str] = {}
    problems: list[str] = []
    for part in re.split(r"[;\n]", value):
        token = part.strip()
        if not token:
            continue
        if "=" not in token:
            problems.append(f"column role is not written as role=column: {token}")
            continue
        role, _, column = token.partition("=")
        role_key = normalize(role)
        if role_key not in validate_dataset.ROLE_FLAGS:
            problems.append(
                f"unknown column role {role.strip()}; use one of "
                + ", ".join(validate_dataset.ROLE_FLAGS)
            )
            continue
        if not column.strip():
            problems.append(f"column role {role_key} names no column")
            continue
        if role_key in roles:
            problems.append(f"column role {role_key} is declared twice")
            continue
        roles[role_key] = column.strip()
    return roles, problems


def artifact_ids(path: Path) -> set[str]:
    """Artifact IDs the record claims fit for, for cross-file checks."""
    _, headers, rows = load_table(path, REQUIRED)
    mapping = normalized_mapping(headers, REQUIRED)
    identifiers: set[str] = set()
    for raw in rows:
        value = normalized_row(raw, mapping)["artifact id"]
        if is_placeholder(value):
            continue
        try:
            identifiers.update(parse_identifier_list(value, field_name="artifact"))
        except ValueError:
            continue
    return identifiers


def check_dataset(row: dict[str, str], label: str, record_dir: Path) -> list[str]:
    """Resolve, hash-verify, and recheck one row's dataset."""
    issues: list[str] = []
    representation = normalize(row["representation"])
    known_representation = representation in validate_dataset.REPRESENTATIONS
    roles, role_problems = parse_roles(row["column roles"])
    issues.extend(f"{label}: {problem}" for problem in role_problems)

    if is_placeholder(row["dataset file"]):
        return issues + [
            f"{label}: missing dataset file; the fit claim cannot be rechecked "
            "without the exact file students receive"
        ]
    try:
        dataset = local_reference_path(row["dataset file"], record_dir)
    except (OSError, RuntimeError) as exc:
        return issues + [
            f"{label}: cannot resolve dataset {row['dataset file']}: {exc}"
        ]
    if dataset is None:
        return issues + [
            f"{label}: dataset file is not a local path: {row['dataset file']}; "
            "record the exact file so the claim can be rechecked"
        ]
    if not dataset.exists():
        return issues + [
            f"{label}: declared dataset is not present: {row['dataset file']}; "
            "the recorded fit claim cannot be rechecked"
        ]

    # The hash is the only check that sees a dataset whose values moved while
    # its columns held still, which no structural check can detect.
    recorded_hash = normalize(row["dataset sha-256"])
    if is_placeholder(recorded_hash):
        issues.append(
            f"{label}: missing dataset SHA-256; without it a dataset can change "
            "its values and still pass every structural check"
        )
    elif not SHA256_PATTERN.match(recorded_hash):
        issues.append(
            f"{label}: dataset SHA-256 is not a 64-character hex digest: "
            f"{row['dataset sha-256']}"
        )
    else:
        try:
            actual = file_digest(dataset)
        except OSError as exc:
            return issues + [f"{label}: cannot hash {row['dataset file']}: {exc}"]
        if actual != recorded_hash:
            issues.append(
                f"{label}: dataset has changed since the check was recorded "
                f"(recorded {recorded_hash[:12]}…, found {actual[:12]}…); the "
                "recorded result is void until the operation is executed again"
            )

    sheet = row["worksheet"].strip()
    is_workbook = dataset.suffix.casefold() in WORKBOOK_SUFFIXES
    if is_workbook and is_placeholder(sheet):
        issues.append(
            f"{label}: missing worksheet; name the sheet even when the workbook "
            "has one today, so adding a sheet later cannot move the check"
        )
    elif not is_workbook and not is_placeholder(sheet):
        issues.append(
            f"{label}: worksheet {sheet} declared for a non-workbook dataset"
        )

    if not known_representation:
        return issues
    # Recheck, do not trust. Roles are strict here: an inferred role confirms
    # that some column of the right kind exists, not the one the activity names.
    dataset_errors, dataset_issues = validate_dataset.validate(
        dataset,
        representation,
        {role: roles.get(role) for role in validate_dataset.ROLE_FLAGS},
        sheet=sheet or None,
        strict_roles=True,
    )
    issues.extend(f"{label}: dataset cannot be read: {item}" for item in dataset_errors)
    issues.extend(
        f"{label}: rechecking the recorded claim failed: {item}"
        for item in dataset_issues
    )
    return issues


def validate(path: Path) -> tuple[list[str], list[str]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [str(exc)], []
    if not any(line.lstrip().startswith("|") for line in text.splitlines()):
        return [], ["Data-task record has no records table; no fit claim is recorded"]
    try:
        _, headers, raw_rows = load_table(path, REQUIRED)
        mapping = normalized_mapping(headers, REQUIRED)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    issues: list[str] = []
    rows = [
        (number, normalized_row(raw, mapping))
        for number, raw in enumerate(raw_rows, start=1)
    ]
    populated = [
        (number, row)
        for number, row in rows
        if any(not is_placeholder(row[field]) for field in REQUIRED)
    ]
    if not populated:
        return [], [
            "Data-task record contains no filled rows; an unfilled record supports "
            "no fit claim"
        ]

    seen: set[str] = set()
    for number, row in populated:
        label = row["artifact id"] or f"Row {number}"
        if is_placeholder(row["artifact id"]):
            issues.append(f"Row {number}: missing artifact ID")
        else:
            try:
                ids = parse_identifier_list(row["artifact id"], field_name="artifact")
                if len(ids) != 1:
                    issues.append(
                        f"{label}: artifact ID must contain exactly one identifier"
                    )
                else:
                    key = next(iter(ids))
                    if key in seen:
                        issues.append(f"{label}: duplicate artifact ID")
                    seen.add(key)
            except ValueError as exc:
                issues.append(f"{label}: {exc}")

        for field in ALWAYS_REQUIRED:
            if is_placeholder(row[field]):
                issues.append(f"{label}: missing {field}")

        method = normalize(row["execution method"])
        if is_placeholder(method):
            issues.append(f"{label}: missing execution method")
        elif method not in EXECUTION_METHODS:
            issues.append(
                f"{label}: unknown execution method {row['execution method']}; use "
                + ", ".join(sorted(EXECUTION_METHODS))
            )
        evidence = row["execution evidence"]
        if method == "code" and is_placeholder(evidence):
            issues.append(
                f"{label}: execution method code without execution evidence; point "
                "to the produced chart, notebook, or output"
            )
        elif not is_placeholder(evidence):
            try:
                target = local_reference_path(evidence, path.parent)
            except (OSError, RuntimeError) as exc:
                issues.append(f"{label}: cannot resolve execution evidence: {exc}")
            else:
                if target is not None and not target.exists():
                    issues.append(
                        f"{label}: execution evidence does not exist: {evidence}"
                    )

        executed_on = row["executed on"]
        if is_placeholder(executed_on):
            issues.append(
                f"{label}: missing executed-on date; a fit claim records when the "
                "operation was actually run"
            )
        elif not parse_iso_date(executed_on):
            issues.append(f"{label}: executed on must use YYYY-MM-DD")

        representation = normalize(row["representation"])
        if is_placeholder(representation):
            issues.append(f"{label}: missing representation")
        elif representation not in validate_dataset.REPRESENTATIONS:
            issues.append(
                f"{label}: unknown representation {row['representation']}; use one of "
                + ", ".join(sorted(validate_dataset.REPRESENTATIONS))
            )

        issues.extend(check_dataset(row, label, path.parent))

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path)
    return emit_report(
        args.path,
        errors,
        issues,
        issue_label="GAP",
        ok_message=(
            "every recorded claim rechecks against an unchanged dataset; the "
            "recorded results themselves still require review"
        ),
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
