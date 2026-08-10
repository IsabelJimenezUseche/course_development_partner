#!/usr/bin/env python3
"""Validate a portable course-design brief.

Exit codes:
  0: structurally complete with no unresolved placeholders
  1: file or structural error
  2: structurally valid but incomplete
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _tabular import emit_report, fold_lookalikes

REQUIRED_H2 = (
    "course context",
    "intended learning",
    "access, participation, and belonging",
    "constraints",
    "implementation load",
    "collaboration",
    "status",
)
REQUIRED_H3 = ("confirmed", "assumed", "open", "current phase", "next decision")
PROFILE_REQUIRED_FIELDS = {
    "establish": (
        "engagement tier",
        "course or module",
        "learning outcomes",
        "interaction level",
        "requested artifacts",
    ),
    "produce": (
        "engagement tier",
        "course or module",
        "learning outcomes",
        "technology and format",
        "interaction level",
        "requested artifacts",
        "minimum viable fallback",
    ),
    "handoff": (
        "engagement tier",
        "course or module",
        "learning outcomes",
        "technology and format",
        "interaction level",
        "requested artifacts",
        "minimum viable fallback",
        "accessibility contact, review, procurement, or exception process",
    ),
}
VALID_ENGAGEMENT_TIERS = {"focused", "project", "course"}

# Handoff is where a brief stops being a working document and becomes the thing
# the next person relies on. These fields change what may be built and how it may
# be graded, so at handoff each needs an answer of some kind — a real value, an
# explicit not-applicable with a reason, or a named owner it is waiting on. A
# blank is none of those; it reads as "nobody considered this".
HANDOFF_SECTIONS = (
    "team and collaborative work",
    "safety authority when physical hazards are involved",
)
HANDOFF_CONSEQUENTIAL = (
    "student population",
    "delivery mode",
    "required technical accessibility target",
    "permitted collaboration, resources, and ai use",
    "how scores combine into a course grade",
    "revision, resubmission, retake, or replacement policy",
    "student workload expectation",
)
# Yes/no fields whose answer decides whether a whole block below applies.
CONDITIONAL_HANDOFF = (
    (
        "physical hazards present",
        (
            "responsible safety owner and role",
            "governing institutional safety document, version, and date",
            "approval status before student use",
        ),
    ),
    (
        "collaborative or team work required",
        (
            "team formation basis and rationale",
            "how team and individual performance each reach the grade",
            "peer-evaluation instrument and its bounded grade effect",
            "escalation path for non-participation or conflict",
        ),
    ),
)
NOT_APPLICABLE = re.compile(r"^not applicable\s*[—-]\s*\S.+", re.IGNORECASE)
AWAITING_OWNER = re.compile(r"^not yet supplied by\s+\S.+", re.IGNORECASE)
TEMPLATE_CHOICE = re.compile(r"^[\w\s/-]+(?:\s*\|\s*[\w\s/-]+)+$")


def is_answered(value: str) -> bool:
    """A real value, an explicit not-applicable, or a named owner it awaits."""
    stripped = value.strip()
    if not stripped:
        return False
    if TEMPLATE_CHOICE.match(stripped):
        # "yes | no | undecided" is the prompt still sitting there.
        return False
    if stripped.startswith("[") and stripped.endswith("]"):
        return False
    return bool(
        NOT_APPLICABLE.match(stripped)
        or AWAITING_OWNER.match(stripped)
        or len(stripped) > 1
    )


def decided_yes_no(value: str) -> str | None:
    """`yes`/`no` only; `undecided` and the untouched prompt are neither."""
    token = value.strip().casefold()
    return token if token in {"yes", "no"} else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate required sections and completion state in course-design-brief.md.",
        epilog=("Example:\n" "  validate_design_state.py course-design-brief.md"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path", type=Path, help="Path to a Markdown course-design brief"
    )
    parser.add_argument(
        "--profile",
        choices=tuple(PROFILE_REQUIRED_FIELDS),
        default="establish",
        help="Completion profile to apply (default: establish)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON for programmatic callers",
    )
    return parser.parse_args()


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", fold_lookalikes(value).strip().lower())


def section_body(text: str, heading: str, level: int) -> str:
    hashes = "#" * level
    pattern = (
        rf"^{hashes}\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^#{{1,{level}}}\s+|\Z)"
    )
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return match.group("body").strip() if match else ""


# Horizontal whitespace only. `\s` also matches a newline, and with MULTILINE `$`
# closing at any line end, a blank field's trailing run crossed into the following
# line and consumed it, so that field was never scanned. An empty field silently
# swallowed the field beneath it.
FIELD_LINE = re.compile(r"^[ \t]*-[ \t]+([^:\n]+):[ \t]*(.*?)[ \t]*$")


def field_lines(text: str) -> tuple[dict[str, tuple[str, int]], set[str]]:
    """Map each bullet field to its value and 1-based line number.

    Scanned one line at a time so a match can never span lines, and so findings can
    say where they came from. Told only that "a field is unanswered" in a 67-field
    template, neither an instructor nor an agent can act on it.
    """
    values: dict[str, tuple[str, int]] = {}
    duplicates: set[str] = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        match = FIELD_LINE.match(line)
        if not match:
            continue
        field = normalize_heading(match.group(1))
        if field in values:
            duplicates.add(field)
        values[field] = (match.group(2).strip(), lineno)
    return values, duplicates


def field_values(text: str) -> tuple[dict[str, str], set[str]]:
    located, duplicates = field_lines(text)
    return {field: value for field, (value, _) in located.items()}, duplicates


def validate_detailed(
    path: Path, profile: str = "establish"
) -> tuple[list[str], list[str], list[str]]:
    """Return (errors, blocking gaps, advisory notes) for one brief at one phase."""
    if not path.is_file():
        return [f"File does not exist: {path}"], [], []

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read {path}: {exc}"], [], []

    heading_records = [
        (len(match.group(1)), normalize_heading(match.group(2)))
        for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, flags=re.MULTILINE)
    ]
    counts: dict[tuple[int, str], int] = {}
    for record in heading_records:
        counts[record] = counts.get(record, 0) + 1
    errors: list[str] = []
    for heading in REQUIRED_H2:
        if (2, heading) not in counts:
            errors.append(f"Missing required level-2 heading: {heading}")
        elif counts[(2, heading)] > 1:
            errors.append(f"Duplicate required heading: {heading}")
    for heading in REQUIRED_H3:
        if (3, heading) not in counts:
            errors.append(f"Missing required level-3 heading: {heading}")
        elif counts[(3, heading)] > 1:
            errors.append(f"Duplicate required heading: {heading}")

    status_start = re.search(
        r"^##\s+Status\s*$", text, flags=re.IGNORECASE | re.MULTILINE
    )
    if status_start:
        trailing = text[status_start.end() :]
        next_h2 = re.search(r"^##\s+", trailing, flags=re.MULTILINE)
        status_text = trailing[: next_h2.start()] if next_h2 else trailing
        for heading in REQUIRED_H3:
            if not re.search(
                rf"^###\s+{re.escape(heading)}\s*$", status_text, flags=re.I | re.M
            ):
                errors.append(f"Status subsection is outside Status: {heading}")

    incomplete: list[str] = []
    # Report each placeholder where it is, so the reader can go straight to it.
    placeholder_patterns = (
        (r"\b(?:TODO|TBD)\b", "Contains TODO/TBD marker"),
        (r"^[ \t]*-[ \t]*$", "Contains an empty list item"),
    )
    for pattern, message in placeholder_patterns:
        hits = [
            lineno
            for lineno, line in enumerate(text.splitlines(), 1)
            if re.search(pattern, line, flags=re.IGNORECASE)
        ]
        if hits:
            shown = ", ".join(str(n) for n in hits[:5])
            more = f" (+{len(hits) - 5} more)" if len(hits) > 5 else ""
            incomplete.append(f"{message} on line {shown}{more}")

    # A field the current phase does not ask for is not yet a gap. An instructor at
    # `establish` may legitimately not know their fallback plan or accessibility
    # contact; those belong to `produce` and `handoff`. Blanks outside the phase's
    # own list are recorded so nothing is lost, but they do not withhold the pass.
    located_fields, _ = field_lines(text)
    required_now = set(PROFILE_REQUIRED_FIELDS[profile])
    notes: list[str] = []
    deferred = sorted(
        (lineno, field)
        for field, (value, lineno) in located_fields.items()
        if not value and field not in required_now
    )
    for lineno, field in deferred[:8]:
        notes.append(f"Unanswered field on line {lineno}: {field}")
    if len(deferred) > 8:
        notes.append(
            f"{len(deferred) - 8} further fields are unanswered and not required "
            f"for {profile}"
        )

    if profile == "handoff":
        for heading in HANDOFF_SECTIONS:
            if (2, heading) not in counts:
                errors.append(f"Missing required level-2 heading: {heading}")
        for name in HANDOFF_CONSEQUENTIAL:
            located = located_fields.get(name)
            if located is None:
                incomplete.append(f"Handoff requires the field: {name}")
            elif not is_answered(located[0]):
                incomplete.append(
                    f"Handoff leaves a consequential field unanswered on line "
                    f"{located[1]}: {name}. Give a value, `not applicable — reason`, "
                    "or `not yet supplied by [owner]` and record it under Open"
                )
        for trigger, dependents in CONDITIONAL_HANDOFF:
            located = located_fields.get(trigger)
            if located is None:
                incomplete.append(f"Handoff requires the field: {trigger}")
                continue
            answer = decided_yes_no(located[0])
            if answer is None:
                incomplete.append(
                    f"Handoff needs a yes or no on line {located[1]}: {trigger}"
                )
                continue
            if answer != "yes":
                continue
            for name in dependents:
                dependent = located_fields.get(name)
                if dependent is None:
                    incomplete.append(
                        f"{trigger} is yes, so the brief requires the field: {name}"
                    )
                elif not is_answered(dependent[0]):
                    incomplete.append(
                        f"{trigger} is yes, so line {dependent[1]} must be answered: "
                        f"{name}"
                    )

    for heading in REQUIRED_H3:
        body = section_body(text, heading, 3)
        if (3, heading) in counts and not re.search(
            r"\w", re.sub(r"^[\s-]+$", "", body)
        ):
            incomplete.append(f"Section is empty: {heading}")

    values, duplicate_fields = field_values(text)
    if any(re.fullmatch(r"\[[^\]\n]+\]", value) for value in values.values()):
        incomplete.append("Contains bracketed placeholder")
    tracked_fields = {
        field
        for required_fields in PROFILE_REQUIRED_FIELDS.values()
        for field in required_fields
    }
    for field in sorted(duplicate_fields & tracked_fields):
        errors.append(f"Duplicate scalar field: {field}")
    headings_present = {name for _, name in heading_records}
    for field in PROFILE_REQUIRED_FIELDS[profile]:
        value, lineno = located_fields.get(field, ("", 0))
        where = f" on line {lineno}" if lineno else " (field is absent)"
        if not value:
            if lineno:
                incomplete.append(
                    f"Required field is unanswered for {profile}: {field}{where}"
                )
            elif field in headings_present:
                # The value is in the document, written as a section instead of
                # a field. Reporting this as "absent" sends an agent off to
                # write the answer again — which is what a real run did, three
                # times in one turn — so name the shape mismatch instead.
                incomplete.append(
                    f"Required field for {profile} is written as a heading rather "
                    f'than a field: {field}. Expected a "- {field.capitalize()}: '
                    '<value>" line; found a heading with that name. Move the '
                    "value onto the field line; the section may stay."
                )
            else:
                incomplete.append(
                    f"Required field is unanswered for {profile}: {field}{where}. "
                    f'Expected a "- {field.capitalize()}: <value>" line'
                )
        elif normalize_heading(value) in {"n/a", "na", "not applicable"}:
            incomplete.append(
                f"Not-applicable field requires a rationale: {field}{where}"
            )

    engagement_tier = normalize_heading(values.get("engagement tier", ""))
    if engagement_tier and engagement_tier not in VALID_ENGAGEMENT_TIERS:
        incomplete.append(f"Unknown engagement tier: {values['engagement tier']}")

    return errors, sorted(set(incomplete)), sorted(set(notes))


def validate(path: Path, profile: str = "establish") -> tuple[list[str], list[str]]:
    """Blocking findings only, for callers that judge pass or fail.

    Advisory notes are dropped here on purpose: a caller asking "does this brief
    clear its phase" should not be told no because a later phase's field is blank.
    """
    errors, incomplete, _ = validate_detailed(path, profile)
    return errors, incomplete


def main() -> int:
    args = parse_args()
    errors, incomplete, notes = validate_detailed(args.path, args.profile)
    return emit_report(
        args.path,
        errors,
        incomplete,
        issue_label="INCOMPLETE",
        ok_message=f"structurally complete course-design brief for profile {args.profile}; manual design review still required: {args.path}",
        as_json=args.json,
        notes=notes,
    )


if __name__ == "__main__":
    sys.exit(main())
