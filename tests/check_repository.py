#!/usr/bin/env python3
"""Check local Markdown links and runtime package inventory.

Exit codes:
  0: repository checks pass
  1: missing checker input or unreadable file
  2: broken local link, package drift, or unrouted resource
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "course-development-partner"
DEFAULT_INVENTORY = ROOT / "tests" / "package-inventory.txt"
ARCHIVE = ROOT / "course-development-partner.zip"
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REMOTE_SCHEMES = {"http", "https", "mailto", "data", "app", "plugin"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check repository-local Markdown links and runtime package inventory.",
        epilog=(
            "Examples:\n"
            "  python3 tests/check_repository.py\n"
            "  python3 tests/check_repository.py --inventory tests/package-inventory.txt"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Expected runtime package inventory, relative to the repository root",
    )
    return parser.parse_args()


def markdown_files() -> list[Path]:
    paths = list(ROOT.glob("*.md"))
    paths.extend(SKILL_ROOT.rglob("*.md"))
    paths.extend((ROOT / "tests").rglob("*.md"))
    return sorted({path for path in paths if path.is_file()})


def target_from_markdown(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    return value.split(maxsplit=1)[0]


def check_links() -> list[str]:
    issues: list[str] = []
    for source in markdown_files():
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(f"Cannot read {source.relative_to(ROOT)}: {exc}")
            continue
        for raw in LINK_PATTERN.findall(text):
            target = target_from_markdown(raw)
            parsed = urlparse(target)
            if not target or target.startswith("#") or parsed.scheme in REMOTE_SCHEMES:
                continue
            path_text = unquote(parsed.path)
            if not path_text:
                continue
            candidate = (source.parent / path_text).resolve()
            if not candidate.exists():
                issues.append(
                    f"Broken local link in {source.relative_to(ROOT)}: {target}"
                )
    return issues


def actual_inventory() -> list[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in SKILL_ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


def check_package_archive() -> tuple[list[str], list[str]]:
    """The tracked upload zip must carry the package it claims to be.

    The zip is a build artifact tracked so it can be uploaded directly, which
    means it ships whatever it last contained. Nothing else in this checker
    looks inside it, so a zip built before a reference or validator was added
    passes every other gate while shipping a package without it.

    Membership is not enough: a zip holding every expected filename with stale
    contents ships the same defect under a passing check, which is how an
    autofix pass over two validators slipped through the first version of this
    function. Compare the bytes.
    """
    if not ARCHIVE.is_file():
        return [], []
    try:
        with zipfile.ZipFile(ARCHIVE) as archive:
            packaged = {
                name: archive.read(name)
                for name in archive.namelist()
                if not name.endswith("/")
            }
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"Cannot read {ARCHIVE.name}: {exc}"], []

    expected = set(actual_inventory())
    issues = [
        f"{ARCHIVE.name} is missing packaged file: {path}"
        for path in sorted(expected - set(packaged))
    ]
    issues.extend(
        f"{ARCHIVE.name} contains unpackaged file: {path}"
        for path in sorted(set(packaged) - expected)
    )
    for path in sorted(expected & set(packaged)):
        try:
            if (ROOT / path).read_bytes() != packaged[path]:
                issues.append(f"{ARCHIVE.name} holds a stale copy of: {path}")
        except OSError as exc:
            return [f"Cannot read {path}: {exc}"], issues
    if issues:
        issues.append(
            f"Rebuild it: rm -f {ARCHIVE.name} && zip -r -X {ARCHIVE.name} "
            f"{SKILL_ROOT.name} -x '*.DS_Store'"
        )
    return [], issues


def check_inventory(inventory_path: Path) -> tuple[list[str], list[str]]:
    if not inventory_path.is_absolute():
        inventory_path = ROOT / inventory_path
    if not inventory_path.is_file():
        return [f"Inventory file does not exist: {inventory_path}"], []
    try:
        expected = sorted(
            line.strip()
            for line in inventory_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read inventory {inventory_path}: {exc}"], []

    actual = actual_inventory()
    issues = [f"Package inventory missing expected file: {path}" for path in expected if path not in actual]
    issues.extend(f"Package inventory has unrecorded file: {path}" for path in actual if path not in expected)

    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    reference_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((SKILL_ROOT / "references").glob("*.md"))
    )
    routed_text = f"{skill_text}\n{reference_text}"

    for path in sorted((SKILL_ROOT / "references").glob("*.md")):
        token = f"references/{path.name}"
        if token not in skill_text:
            issues.append(f"Reference is not routed from SKILL.md: {token}")
    for path in sorted((SKILL_ROOT / "assets").glob("*.md")):
        token = f"assets/{path.name}"
        if token not in routed_text:
            issues.append(f"Asset is not routed from SKILL.md or a direct reference: {token}")
    for path in sorted((SKILL_ROOT / "scripts").glob("validate_*.py")):
        token = f"scripts/{path.name}"
        if token not in skill_text:
            issues.append(f"Validator is not named in SKILL.md: {token}")

    return [], issues


def main() -> int:
    args = parse_args()
    errors, inventory_issues = check_inventory(args.inventory)
    archive_errors, archive_issues = check_package_archive()
    errors.extend(archive_errors)
    issues = check_links() + inventory_issues + archive_issues
    for item in errors:
        print(f"ERROR: {item}")
    for item in issues:
        print(f"ISSUE: {item}")
    if errors:
        return 1
    if issues:
        return 2
    print("OK: repository links, package inventory, and packaged archive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
