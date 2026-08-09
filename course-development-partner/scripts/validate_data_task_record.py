#!/usr/bin/env python3
"""Re-execute the fit claims recorded in a data-task record.

A validation token in the artifact manifest is a claim that somebody executed
the requested operation on the exact supplied dataset. On its own it is
self-attested: nothing distinguishes a row where the work happened from a row
where the token was typed. This validator removes that gap by re-running each
recorded claim against the dataset it names, using the same checks as
``validate_dataset.py``.

A row that cannot be re-executed — an absent dataset, an unknown
representation, unparseable roles — is reported as a gap, because an
unverifiable claim and a false one are indistinguishable to the reader.

What it still cannot do: confirm that the produced output answers the question
students were asked, or that the intended interpretation follows from it. Those
stay with a qualified human, as ``references/data-task-fit.md`` says.

Exit codes:
  0: every recorded claim re-executes against its dataset
  1: file, parsing, or structural error
  2: fit-record gaps detected
"""

from __future__ import annotations

import argparse
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
    "dataset version or date",
    "representation",
    "column roles",
    "expected student output",
    "intended interpretation",
    "execution method",
    "executed on",
    "result",
)

EXECUTION_METHODS = {"validator", "code", "manual"}
# Values that look filled in but assert nothing.
PLACEHOLDERS = {"", "-", "tbd", "todo", "n/a", "na", "none", "?", "pending"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Re-run each recorded data-task fit claim against the dataset it names."
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

        for field in (
            "dataset version or date",
            "expected student output",
            "intended interpretation",
            "result",
        ):
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
        executed_on = row["executed on"]
        if is_placeholder(executed_on):
            issues.append(
                f"{label}: missing executed-on date; a fit claim records when the "
                "operation was actually run"
            )
        elif not parse_iso_date(executed_on):
            issues.append(f"{label}: executed on must use YYYY-MM-DD")

        representation = normalize(row["representation"])
        known_representation = representation in validate_dataset.REPRESENTATIONS
        if is_placeholder(representation):
            issues.append(f"{label}: missing representation")
        elif not known_representation:
            issues.append(
                f"{label}: unknown representation {row['representation']}; use one of "
                + ", ".join(sorted(validate_dataset.REPRESENTATIONS))
            )

        roles, role_problems = parse_roles(row["column roles"])
        for problem in role_problems:
            issues.append(f"{label}: {problem}")

        if is_placeholder(row["dataset file"]):
            issues.append(
                f"{label}: missing dataset file; the fit claim cannot be re-executed "
                "without the exact file students receive"
            )
            continue
        try:
            dataset = local_reference_path(row["dataset file"], path.parent)
        except (OSError, RuntimeError) as exc:
            issues.append(f"{label}: cannot resolve dataset {row['dataset file']}: {exc}")
            continue
        if dataset is None:
            issues.append(
                f"{label}: dataset file is not a local path: {row['dataset file']}; "
                "record the exact file so the claim can be re-executed"
            )
            continue
        if not dataset.exists():
            issues.append(
                f"{label}: declared dataset is not present: {row['dataset file']}; "
                "the recorded fit claim cannot be re-executed"
            )
            continue
        if not known_representation:
            continue
        # The claim is re-run, not read. A row that passed when it was written and
        # broke when the dataset changed fails here.
        dataset_errors, dataset_issues = validate_dataset.validate(
            dataset,
            representation,
            {role: roles.get(role) for role in validate_dataset.ROLE_FLAGS},
        )
        for item in dataset_errors:
            issues.append(f"{label}: dataset cannot be read: {item}")
        for item in dataset_issues:
            issues.append(f"{label}: re-executing the recorded claim failed: {item}")

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
            "every recorded fit claim re-executes against its dataset; whether the "
            "result answers the student's question still requires review"
        ),
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
