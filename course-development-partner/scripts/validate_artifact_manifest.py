#!/usr/bin/env python3
"""Validate an educational artifact manifest.

Exit codes:
  0: valid and complete
  1: file, parsing, or structural error
  2: readiness or consistency issues detected
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = (
    "artifact id",
    "file or reference",
    "audience",
    "outcome(s)",
    "status",
    "validation completed",
    "blockers/open issues",
    "last reviewed",
)
VALID_STATUSES = {"draft", "review", "validated", "teaching-ready", "retired"}
EMPTY_ISSUES = {"", "-", "none", "n/a", "na"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required fields and teaching-readiness claims in an artifact manifest."
    )
    parser.add_argument("path", type=Path, help="Path to artifact-manifest.md or a CSV equivalent")
    parser.add_argument(
        "--check-paths",
        action="store_true",
        help="Verify local file references relative to the manifest directory",
    )
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def markdown_rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    for index in range(len(lines) - 1):
        header = [cell.strip() for cell in lines[index].strip("|").split("|")]
        separator = [cell.strip() for cell in lines[index + 1].strip("|").split("|")]
        if len(header) == len(separator) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
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


def is_local_reference(value: str) -> bool:
    if not value or value.startswith(("#", "[")):
        return False
    parsed = urlparse(value)
    return not parsed.scheme and not parsed.netloc


def validate(path: Path, check_paths: bool = False) -> tuple[list[str], list[str]]:
    try:
        headers, raw_rows = load_rows(path)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)], []

    mapping = {normalize(header): header for header in headers}
    missing = [column for column in REQUIRED if column not in mapping]
    if missing:
        return [f"Missing required column: {column}" for column in missing], []
    if not raw_rows:
        return [], ["Artifact manifest contains no data rows"]

    issues: list[str] = []
    seen_ids: set[str] = set()
    for row_number, raw in enumerate(raw_rows, start=1):
        row = {key: (raw.get(original) or "").strip() for key, original in mapping.items()}
        artifact_id = row["artifact id"]
        label = artifact_id or f"row {row_number}"

        if not artifact_id:
            issues.append(f"Row {row_number}: missing artifact ID")
        else:
            normalized_id = normalize(artifact_id)
            if normalized_id in seen_ids:
                issues.append(f"Row {row_number}: duplicate artifact ID {artifact_id}")
            seen_ids.add(normalized_id)

        for field in ("file or reference", "audience", "outcome(s)", "status"):
            if not row[field]:
                issues.append(f"{label}: missing {field}")

        status = normalize(row["status"])
        if status and status not in VALID_STATUSES:
            issues.append(f"{label}: unknown status {row['status']}")
        if status in {"validated", "teaching-ready"} and not row["validation completed"]:
            issues.append(f"{label}: {status} without validation evidence")
        if status == "teaching-ready":
            if normalize(row["blockers/open issues"]) not in EMPTY_ISSUES:
                issues.append(f"{label}: teaching-ready with unresolved blockers/open issues")
            if not row["last reviewed"]:
                issues.append(f"{label}: teaching-ready without last-reviewed date")

        reference = row["file or reference"]
        if check_paths and is_local_reference(reference):
            target = (path.parent / reference).resolve()
            if not target.exists():
                issues.append(f"{label}: local reference does not exist: {reference}")

    return [], issues


def main() -> int:
    args = parse_args()
    errors, issues = validate(args.path, args.check_paths)
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"ISSUE: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
