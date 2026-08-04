#!/usr/bin/env python3
"""Shared parsing and validation helpers for portable course-design tables."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9][A-Za-z0-9_-]*$")
REMOTE_SCHEMES = {"http", "https", "mailto", "data", "app", "plugin"}

# Ordinal cognitive-demand vocabulary shared by the alignment map, the assessment
# blueprint, and cross-file demand-match checks. Ranks are comparable; higher means
# a more demanding target. Instructors using SOLO, Depth of Knowledge, or a
# discipline-specific scale map their level onto these tokens in the state files.
COGNITIVE_DEMANDS: dict[str, int] = {
    "remember": 1,
    "understand": 2,
    "apply": 3,
    "analyze": 4,
    "evaluate": 5,
    "create": 6,
}


# Typographic characters that look like their ASCII counterparts and routinely arrive
# in generated Markdown: a column heading written with a non-breaking hyphen reads as
# identical to a human and fails an exact match. Folded for comparison only, so the
# file's own text is never rewritten and error messages still echo what was written.
LOOKALIKE_CHARACTERS = {
    "‐": "-",  # hyphen
    "‑": "-",  # non-breaking hyphen
    "‒": "-",  # figure dash
    "–": "-",  # en dash
    "—": "-",  # em dash
    "−": "-",  # minus sign
    " ": " ",  # no-break space
    " ": " ",  # narrow no-break space
    "‘": "'",  # left single quote
    "’": "'",  # right single quote
    "“": '"',  # left double quote
    "”": '"',  # right double quote
}
_LOOKALIKE_TABLE = str.maketrans(LOOKALIKE_CHARACTERS)


def fold_lookalikes(value: str) -> str:
    """Map typographic look-alikes onto ASCII so matching compares meaning, not glyphs."""
    return value.translate(_LOOKALIKE_TABLE)


# Shared across every validator: 0 clean, 1 hard errors, 2 gaps or incompleteness.
# A gap is a design step not taken yet; an error is a file that could not be read as
# claimed. Keeping them apart is the difference between "finish this" and "fix this".
EXIT_PASS = 0
EXIT_ERROR = 1
EXIT_INCOMPLETE = 2


def emit_report(
    path: object,
    errors: list[str],
    issues: list[str],
    *,
    issue_label: str,
    ok_message: str,
    as_json: bool = False,
    notes: list[str] | None = None,
) -> int:
    """Print one validator's findings and return its exit code.

    The text form is unchanged. The JSON form exists because a caller driving these
    scripts in a loop should not have to parse prose and infer the exit convention;
    it reads the same findings as data.
    """
    # Notes are advisory and never change the verdict: they record work that belongs
    # to a later phase, which is not the same as work left undone in this one.
    notes = notes or []
    code = EXIT_ERROR if errors else (EXIT_INCOMPLETE if issues else EXIT_PASS)
    if as_json:
        findings = [{"level": "error", "message": item} for item in errors]
        findings += [
            {"level": issue_label.lower(), "message": item} for item in issues
        ]
        findings += [{"level": "note", "message": item} for item in notes]
        print(
            json.dumps(
                {
                    "path": str(path),
                    "status": {
                        EXIT_PASS: "pass",
                        EXIT_ERROR: "fail",
                        EXIT_INCOMPLETE: "incomplete",
                    }[code],
                    "exit_code": code,
                    "findings": findings,
                    "summary": ok_message if code == EXIT_PASS else "",
                },
                indent=2,
            )
        )
        return code
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"{issue_label}: {item}")
    for item in notes:
        print(f"NOTE: {item}")
    if code == EXIT_PASS:
        print(f"OK: {ok_message}")
    return code


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", fold_lookalikes(value).strip().lower())


def parse_cognitive_demand(value: str) -> int | None:
    """Return the ordinal rank of a controlled cognitive-demand token, or None."""
    return COGNITIVE_DEMANDS.get(normalize(value))


def cognitive_demand_vocabulary() -> str:
    """Return the controlled tokens in ascending rank order for error messages."""
    return ", ".join(
        sorted(COGNITIVE_DEMANDS, key=lambda token: COGNITIVE_DEMANDS[token])
    )


def split_markdown_row(line: str) -> list[str]:
    """Split a pipe table row while honoring escaped pipes and inline-code pipes."""
    value = line.strip()
    if not value.startswith("|"):
        raise ValueError("Markdown table row must start with |")
    if value.endswith("|"):
        value = value[1:-1]
    else:
        value = value[1:]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    code_delimiter = 0
    index = 0
    while index < len(value):
        char = value[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            escaped = True
            current.append(char)
            index += 1
            continue
        if char == "`":
            run = 1
            while index + run < len(value) and value[index + run] == "`":
                run += 1
            current.extend("`" * run)
            if code_delimiter == 0:
                code_delimiter = run
            elif code_delimiter == run:
                code_delimiter = 0
            index += run
            continue
        if char == "|" and code_delimiter == 0:
            cells.append("".join(current).strip().replace(r"\|", "|"))
            current = []
        else:
            current.append(char)
        index += 1
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip().replace(r"\|", "|"))
    return cells


def _validate_headers(headers: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    duplicates: list[str] = []
    for header in headers:
        key = normalize(header)
        if not key:
            raise ValueError("Table contains an empty header")
        if key in mapping:
            duplicates.append(header)
        mapping[key] = header
    if duplicates:
        raise ValueError(f"Duplicate normalized header: {duplicates[0]}")
    return mapping


def markdown_rows(
    text: str, required_headers: tuple[str, ...]
) -> tuple[list[str], list[dict[str, str]]]:
    lines = text.splitlines()
    candidates: list[tuple[int, list[str], list[dict[str, str]]]] = []
    table_headers_seen: list[list[str]] = []

    for index in range(len(lines) - 1):
        if not lines[index].strip().startswith("|") or not lines[
            index + 1
        ].strip().startswith("|"):
            continue
        try:
            header = split_markdown_row(lines[index])
            separator = split_markdown_row(lines[index + 1])
        except ValueError:
            continue
        if len(header) != len(separator) or not all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in separator
        ):
            continue
        mapping = _validate_headers(header)
        table_headers_seen.append(list(mapping))
        if not set(required_headers) <= set(mapping):
            continue

        rows: list[dict[str, str]] = []
        row_index = index + 2
        while row_index < len(lines) and lines[row_index].strip().startswith("|"):
            cells = split_markdown_row(lines[row_index])
            if len(cells) != len(header):
                raise ValueError(
                    f"Malformed Markdown table row at line {row_index + 1}: "
                    f"expected {len(header)} cells, found {len(cells)}"
                )
            rows.append(dict(zip(header, cells)))
            row_index += 1
        candidates.append((index + 1, header, rows))

    if not candidates:
        if table_headers_seen:
            available = "; ".join(", ".join(headers) for headers in table_headers_seen)
            raise ValueError(
                "No Markdown table contains the required columns. "
                f"Tables found: {available}"
            )
        raise ValueError("No Markdown table found")
    if len(candidates) > 1:
        locations = ", ".join(str(item[0]) for item in candidates)
        raise ValueError(
            f"Multiple Markdown tables match the required schema at lines {locations}"
        )
    _, headers, rows = candidates[0]
    return headers, rows


def load_table(
    path: Path, required_headers: tuple[str, ...]
) -> tuple[str, list[str], list[dict[str, str]]]:
    if not path.is_file():
        raise ValueError(f"File does not exist: {path}")
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            try:
                headers = next(reader)
            except StopIteration as exc:
                raise ValueError("CSV has no header") from exc
            mapping = _validate_headers(headers)
            missing = [header for header in required_headers if header not in mapping]
            if missing:
                raise ValueError(
                    "; ".join(
                        f"Missing required column: {header}" for header in missing
                    )
                )
            rows: list[dict[str, str]] = []
            for row_number, cells in enumerate(reader, start=2):
                if len(cells) != len(headers):
                    raise ValueError(
                        f"Malformed CSV row {row_number}: expected {len(headers)} cells, "
                        f"found {len(cells)}"
                    )
                rows.append(dict(zip(headers, cells)))
            return text, headers, rows
    headers, rows = markdown_rows(text, required_headers)
    return text, headers, rows


def normalized_mapping(headers: list[str], required: tuple[str, ...]) -> dict[str, str]:
    mapping = _validate_headers(headers)
    missing = [column for column in required if column not in mapping]
    if missing:
        raise ValueError(
            "; ".join(f"Missing required column: {column}" for column in missing)
        )
    return mapping


def normalized_row(raw: dict[str, str], mapping: dict[str, str]) -> dict[str, str]:
    return {key: (raw.get(original) or "").strip() for key, original in mapping.items()}


def parse_identifier_list(value: str, *, field_name: str) -> set[str]:
    if "," in value:
        raise ValueError(
            f"invalid {field_name} identifier list uses a comma; "
            "use semicolons between identifiers"
        )
    tokens = [token.strip() for token in value.split(";") if token.strip()]
    if value.strip() and not tokens:
        raise ValueError(
            f"invalid {field_name} identifier list contains no identifiers"
        )
    invalid = [token for token in tokens if not IDENTIFIER_PATTERN.fullmatch(token)]
    if invalid:
        raise ValueError(f"invalid {field_name} identifier {invalid[0]}")
    return {normalize(token) for token in tokens}


def parse_positive_finite(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    return number if number > 0 and math.isfinite(number) else None


def parse_nonnegative_finite(value: str) -> float | None:
    try:
        number = float(value)
    except ValueError:
        return None
    return number if number >= 0 and math.isfinite(number) else None


def parse_iso_date(value: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def find_cycles(graph: dict[str, set[str]]) -> list[str]:
    cycles: set[tuple[str, ...]] = set()
    visiting: list[str] = []
    active: set[str] = set()
    complete: set[str] = set()

    def canonical_cycle(cycle: list[str]) -> tuple[str, ...]:
        core = cycle[:-1]
        rotations = [tuple(core[index:] + core[:index]) for index in range(len(core))]
        canonical = min(rotations)
        return canonical + (canonical[0],)

    def visit(node: str) -> None:
        if node in complete:
            return
        if node in active:
            start = visiting.index(node)
            cycles.add(canonical_cycle(visiting[start:] + [node]))
            return
        active.add(node)
        visiting.append(node)
        for neighbor in sorted(graph.get(node, set())):
            visit(neighbor)
        visiting.pop()
        active.remove(node)
        complete.add(node)

    for node in sorted(graph):
        visit(node)
    return [" -> ".join(cycle) for cycle in sorted(cycles)]


def extract_link_target(value: str) -> str:
    stripped = value.strip()
    match = re.fullmatch(r"!?\[[^\]]*\]\((.+)\)", stripped)
    if match:
        stripped = match.group(1).strip()
        if stripped.startswith("<") and ">" in stripped:
            return stripped[1 : stripped.index(">")]
        stripped = stripped.split(maxsplit=1)[0]
    return stripped


def local_reference_path(value: str, base: Path) -> Path | None:
    target = extract_link_target(value)
    if not target or target.startswith("#"):
        return None
    parsed = urlparse(target)
    if parsed.scheme in REMOTE_SCHEMES or parsed.netloc:
        return None
    path_text = unquote(parsed.path)
    if not path_text:
        return None
    candidate = Path(path_text)
    return candidate if candidate.is_absolute() else (base / candidate).resolve()


def group_by_sequence(rows: list[dict[str, str]]) -> dict[float, list[dict[str, str]]]:
    grouped: dict[float, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[float(row["sequence"])].append(row)
    return dict(sorted(grouped.items()))
