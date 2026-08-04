from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "course-development-partner" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"


def run_script(
    name: str, content: str, suffix: str = ".md", *args: str
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / f"input{suffix}"
        path.write_text(content, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), str(path), *args],
            check=False,
            capture_output=True,
            text=True,
        )


def run_path(name: str, path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def run_help(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )


def run_project(files: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        project = Path(temp_dir)
        for name, content in files.items():
            if "- Schema version:" in content and "- Last updated:" not in content:
                content = re.sub(
                    r"(^\s*-\s*Schema version:\s*\S+\s*$)",
                    r"\1\n- Last updated: 2026-08-01",
                    content,
                    count=1,
                    flags=re.MULTILINE,
                )
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_project.py"), str(project), *args],
            check=False,
            capture_output=True,
            text=True,
        )


class DesignStateValidatorTests(unittest.TestCase):
    def test_complete_design_state_passes(self) -> None:
        content = """# Course Design Brief
- Engagement tier: Project
## Course context
- Course or module: BIO 101
## Intended learning
- Learning outcomes: Explain a mechanism
## Access, participation, and belonging
- Provide equivalent text and visual representations
## Constraints
- Fifty minutes
## Implementation load
- One class period; no new platform
## Collaboration
- Interaction level: Co-design
- Requested artifacts: Alignment map and activity draft
## Status
### Confirmed
- Outcome approved
### Assumed
- Prior knowledge present
### Open
- Accessibility review pending
### Current phase
- Establish alignment
### Next decision
- Select evidence of learning
"""
        result = run_script("validate_design_state.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blank_field_does_not_hide_the_field_below_it(self) -> None:
        """A blank bullet used to swallow the next line, hiding a filled field.

        `\\s` matches newlines and MULTILINE `$` closes at any line end, so the scan
        ran past a blank field and never saw the one beneath it. Real briefs are
        part-filled, so this misfired exactly when it mattered most.
        """
        content = (FIXTURES / "design_state" / "valid.md").read_text(encoding="utf-8")
        # Blank the field directly above a profile-required one.
        content = content.replace(
            "- Engagement tier:", "- Last updated:\n- Engagement tier:"
        )
        result = run_script("validate_design_state.py", content)

        # `Engagement tier` is filled and sits under a blank field; it must be seen.
        self.assertNotIn(
            "unanswered for establish: engagement tier", result.stdout.lower()
        )

    def test_unanswered_fields_are_reported_with_a_location(self) -> None:
        """A bare 'a field is unanswered' is unactionable in a 67-field template."""
        template = (
            ROOT / "course-development-partner" / "assets" / "course-design-brief.md"
        ).read_text()
        result = run_script("validate_design_state.py", template)

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"Unanswered field on line \d+: \S")

    def test_blank_scalar_does_not_capture_the_next_line_as_its_value(self) -> None:
        """A blank `Evidence level claimed:` used to read the following bullet.

        Asserted against the extractor directly. Driving it through the CLI proved
        nothing: the validator reports other problems first, so the wrong value
        never reached stdout and the test passed against the bug.
        """
        sys.path.insert(0, str(SCRIPTS))
        try:
            import validate_assessment_blueprint as blueprint_validator
        finally:
            sys.path.pop(0)

        text = "- Evidence level claimed:\n- Known limitations: none\n"
        value = blueprint_validator.evidence_level(text, [], {})

        self.assertEqual(value, "", f"blank field captured {value!r} from the next line")

    def test_incomplete_design_state_returns_two(self) -> None:
        template = (
            ROOT / "course-development-partner" / "assets" / "course-design-brief.md"
        ).read_text()
        result = run_script("validate_design_state.py", template)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_required_heading_at_wrong_level_is_structural_error(self) -> None:
        content = (FIXTURES / "design_state" / "valid.md").read_text(encoding="utf-8")
        content = content.replace("## Constraints", "### Constraints")
        result = run_script("validate_design_state.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Missing required level-2 heading: constraints", result.stdout)

    def test_duplicate_scalar_field_is_structural_error(self) -> None:
        content = (FIXTURES / "design_state" / "valid.md").read_text(encoding="utf-8")
        content = content.replace(
            "- Engagement tier: Project",
            "- Engagement tier: Project\n- Engagement tier: Course",
        )
        result = run_script("validate_design_state.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Duplicate scalar field: engagement tier", result.stdout)

    def test_legitimate_bracketed_content_is_not_a_placeholder(self) -> None:
        content = (FIXTURES / "design_state" / "valid.md").read_text(encoding="utf-8")
        content = content.replace(
            "Explain a mechanism",
            "Interpret a confidence interval such as [0, 1]",
        )
        result = run_script("validate_design_state.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class AlignmentValidatorTests(unittest.TestCase):
    def test_complete_alignment_passes(self) -> None:
        content = """# Alignment Map
| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | Understand | Annotated diagram | contrasting cases | Comparison activity | Exit ticket | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_alignment_gap_returns_two(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | understand |  | contrasting cases | Comparison activity | Exit ticket | draft |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing evidence of learning", result.stdout)

    def test_empty_and_unknown_statuses_are_both_rejected(self) -> None:
        result = run_path(
            "validate_alignment_map.py", FIXTURES / "alignment" / "invalid.md"
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing status", result.stdout)
        self.assertIn("unknown status done", result.stdout)
        self.assertIn("duplicate outcome ID LO-1", result.stdout)
        self.assertIn("activity or assessment has no outcome ID", result.stdout)

    def test_missing_alignment_fields_and_empty_row_are_reported(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "missing observable learning outcome",
            "missing cognitive demand",
            "missing evidence of learning",
            "missing learning mechanism",
            "missing learning activity/support",
            "missing feedback or assessment",
            "missing status",
            "empty row",
        ):
            self.assertIn(expected, result.stdout)

    def test_parser_selects_schema_table_and_preserves_escaped_pipe(self) -> None:
        content = """| Note | Value |
|---|---|
| Owner | Faculty |

| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Compare A \\| B | analyze | Explanation | contrasting cases | Contrast cases | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_uncontrolled_cognitive_demand_is_reported(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | synthesize | Diagram | contrasting cases | Activity | Exit ticket | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown cognitive demand synthesize", result.stdout)

    def test_every_controlled_cognitive_demand_is_accepted(self) -> None:
        rows = "\n".join(
            f"| LO-{index} | Outcome {index} | {demand} | Evidence | retrieval | Activity | Feedback | approved |"
            for index, demand in enumerate(
                ("remember", "understand", "apply", "analyze", "evaluate", "create"),
                start=1,
            )
        )
        content = (
            "| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning "
            "| Learning mechanism | Learning activity/support | Feedback or assessment | Status |\n"
            "|---|---|---|---|---|---|---|---|\n" + rows + "\n"
        )
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_middle_row_is_structural_error(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain | understand | Evidence | retrieval | Activity | Feedback | approved |
| LO-2 | This row is short | Evidence |
| LO-3 | Apply | apply | Evidence | practice | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Malformed Markdown table row", result.stdout)

    def test_duplicate_normalized_header_is_structural_error(self) -> None:
        content = """| Outcome ID | outcome   id | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|---|
| LO-1 | LO-1 | Explain | understand | Evidence | retrieval | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Duplicate normalized header", result.stdout)

    def test_retired_only_alignment_reports_no_active_outcomes(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain | understand | Explanation | retrieval | Archived activity | Archived feedback | retired |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Alignment map contains no active outcomes", result.stdout)

    def test_status_only_retired_row_requires_an_outcome_id(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | retired |
| LO-1 | Explain | understand | Explanation | retrieval | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("activity or assessment has no outcome ID", result.stdout)

    def test_separator_only_outcome_id_is_reported_without_a_traceback(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| ; | Explain | understand | Explanation | retrieval | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("identifier list contains no identifiers", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


class ArtifactManifestValidatorTests(unittest.TestCase):
    def test_teaching_ready_manifest_passes(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws-1 | student | LO-1 | teaching-ready | technical; alignment; accessibility; reopen | none | 2026-07-31 | not required | https://example.edu/ws-1-accessibility | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_teaching_ready_with_blocker_returns_two(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | worksheet.md | student | LO-1 | teaching-ready | technical; alignment; accessibility; reopen | solution not verified | 2026-07-31 | not required | accessibility-review.md | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unresolved blockers/open issues", result.stdout)

    def test_declared_pair_requires_labeled_student_and_instructor_variants(
        self,
    ) -> None:
        result = run_path(
            "validate_artifact_manifest.py",
            FIXTURES / "artifact_manifest" / "invalid.md",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing a variant label", result.stdout)
        self.assertIn("required instructor variant is not represented", result.stdout)

    def test_complete_declared_pair_passes(self) -> None:
        result = run_path(
            "validate_artifact_manifest.py",
            FIXTURES / "artifact_manifest" / "boundary.md",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_paths_detects_missing_local_reference(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | missing.md | student | LO-1 | draft | manual | none | 2026-07-31 | https://example.edu/not-required | https://example.edu/pending | not required |
"""
        result = run_script(
            "validate_artifact_manifest.py", content, ".md", "--check-paths"
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("local file or reference does not exist", result.stdout)

    def test_check_paths_reports_a_symlink_loop_without_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            (directory / "loop.md").symlink_to("loop.md")
            manifest = directory / "artifact-manifest.md"
            manifest.write_text(
                """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | loop.md | student | LO-1 | draft | manual | none | 2026-08-01 | not required | pending | not required |
""",
                encoding="utf-8",
            )
            result = run_path(
                "validate_artifact_manifest.py",
                manifest,
                "--check-paths",
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("cannot resolve local file or reference", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_fields_validation_evidence_and_family_context_are_reported(
        self,
    ) -> None:
        content = """| Artifact ID | Artifact family | Variant | Required variants | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | student | student; instructor | markdown |  |  |  |  |  | none |  | not required | pending | not required |
| A-2 |  |  |  | markdown | https://example.edu/a-2 | instructor | LO-1 | validated |  | none | 2026-07-31 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "missing artifact ID",
            "missing file or reference",
            "missing audience",
            "missing outcome(s)",
            "missing status",
            "validated without validation evidence",
            "variant or required variants declared without an artifact family",
        ):
            self.assertIn(expected, result.stdout)

    def test_ready_manifest_rejects_none_evidence_and_invalid_date(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-1 | validated | none | none | 2026-13-40 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown validation token none", result.stdout)
        self.assertIn("last reviewed must use YYYY-MM-DD", result.stdout)

    def test_calendar_invalid_iso_date_is_rejected(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-1 | validated | technical; alignment | none | 2026-02-31 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("last reviewed must use YYYY-MM-DD", result.stdout)

    def test_draft_manifest_rejects_a_non_iso_review_date(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-1 | draft | manual | none | not-a-date | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("last reviewed must use YYYY-MM-DD", result.stdout)

    def test_pending_non_file_evidence_is_not_treated_as_a_path_for_drafts(
        self,
    ) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-1 | draft | manual | none | 2026-08-01 | not applicable — plain Markdown | pending | not required |
"""
        result = run_script(
            "validate_artifact_manifest.py", content, ".md", "--check-paths"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_declared_variant_is_required(self) -> None:
        content = """| Artifact ID | Artifact family | Variant | Required variants | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | family-1 | student | student; instructor; solution | markdown | https://example.edu/student | student | LO-1 | draft | manual | none | 2026-07-31 | not required | pending | not required |
| WS-2 | family-1 | instructor | student; instructor; solution | markdown | https://example.edu/instructor | instructor | LO-1 | draft | manual | none | 2026-07-31 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("required solution variant is not represented", result.stdout)

    def test_manifest_requires_artifact_family_schema_columns(self) -> None:
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws | student | LO-1 | draft | manual | none | 2026-08-01 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("No Markdown table contains the required columns", result.stdout)

    MANIFEST_HEADER = (
        "| Artifact ID | Artifact type | Artifact family | Variant | Required variants "
        "| File or reference | Audience | Outcome(s) | Status | Validation completed "
        "| Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    )

    def _teaching_ready_row(self, safety: str) -> str:
        return (
            self.MANIFEST_HEADER
            + "| WS-1 | markdown |  |  |  | https://example.edu/ws-1 | student | LO-1 "
            "| teaching-ready | technical; alignment; accessibility; reopen | none "
            f"| 2026-07-31 | not required | https://example.edu/a11y | {safety} |\n"
        )

    def test_teaching_ready_without_safety_declaration_is_reported(self) -> None:
        result = run_script(
            "validate_artifact_manifest.py", self._teaching_ready_row("")
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("no safety review declaration", result.stdout)

    def test_teaching_ready_accepts_explicit_not_required_safety(self) -> None:
        result = run_script(
            "validate_artifact_manifest.py", self._teaching_ready_row("not required")
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_teaching_ready_accepts_a_linked_safety_review(self) -> None:
        result = run_script(
            "validate_artifact_manifest.py",
            self._teaching_ready_row("[safety](https://example.edu/safety-review)"),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_teaching_ready_distinguishes_prose_from_a_local_review_path(
        self,
    ) -> None:
        prose_result = run_script(
            "validate_artifact_manifest.py",
            self._teaching_ready_row("Approved by EHS. See lab binder"),
        )
        self.assertEqual(
            prose_result.returncode,
            2,
            prose_result.stdout + prose_result.stderr,
        )
        self.assertIn(
            "must be a review reference",
            prose_result.stdout,
        )

        path_result = run_script(
            "validate_artifact_manifest.py",
            self._teaching_ready_row("safety reviews/lab approval.pdf"),
        )
        self.assertEqual(
            path_result.returncode,
            0,
            path_result.stdout + path_result.stderr,
        )

    def test_teaching_ready_rejects_pending_or_bare_safety_status(self) -> None:
        for safety in ("pending", "approved"):
            with self.subTest(safety=safety):
                result = run_script(
                    "validate_artifact_manifest.py",
                    self._teaching_ready_row(safety),
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("teaching-ready", result.stdout)

    def test_manifest_rejects_invalid_artifact_id(self) -> None:
        content = self._teaching_ready_row("not required").replace(
            "| WS-1 | markdown", "| not a valid id | markdown"
        )
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("invalid artifact identifier", result.stdout)

    def test_draft_row_may_leave_safety_review_blank(self) -> None:
        content = (
            self.MANIFEST_HEADER
            + "| WS-1 | markdown |  |  |  | https://example.edu/ws-1 | student | LO-1 "
            "| draft | manual | none | 2026-07-31 | not required | pending |  |\n"
        )
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_retired_variant_does_not_satisfy_active_family_requirement(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-S | markdown | worksheet | student | student; instructor; solution | https://example.edu/student | student | LO-1 | draft | manual | none | 2026-08-01 | not required | pending | not required |
| WS-I | markdown | worksheet | instructor |  | https://example.edu/instructor | instructor | LO-1 | draft | manual | none | 2026-08-01 | not required | pending | not required |
| WS-K | markdown | worksheet | solution |  | old-solution.md | instructor | LO-1 | retired | manual | none | 2026-07-01 | not required | pending | not required |
"""
        result = run_script(
            "validate_artifact_manifest.py",
            content,
            ".md",
            "--check-paths",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("required solution variant is not represented", result.stdout)
        self.assertNotIn("old-solution.md", result.stdout)

    def test_retired_only_manifest_reports_no_active_artifacts(self) -> None:
        content = """| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OLD-1 | markdown |  |  |  | old.md | instructor | LO-1 | retired | manual | none | 2026-07-01 | not required | pending | not required |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Artifact manifest contains no active artifacts", result.stdout)


class AssessmentBlueprintValidatorTests(unittest.TestCase):
    def test_complete_blueprint_passes(self) -> None:
        content = """# Assessment Blueprint
- Assessed outcome scope: LO-1
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Formative feedback | Select and justify a model | Evaluate | Constructed response | independent | 12 | 10 | none identified | approved |
- Evidence level claimed: classroom-reviewed
"""
        result = run_script(
            "validate_assessment_blueprint.py",
            content,
            ".md",
            "--required-outcome",
            "LO-1",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_comma_separated_outcomes_are_rejected_with_separator_help(self) -> None:
        content = """# Assessment Blueprint
- Assessed outcome scope: LO-1; LO-2
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1, LO-2 | Formative feedback | Explain a relationship | Analyze | Constructed response | independent | 12 | 10 | none identified | approved |
- Evidence level claimed: classroom-reviewed
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("use semicolons between identifiers", result.stdout)

    def test_blueprint_detects_missing_coverage_and_overclaim(self) -> None:
        content = """# Assessment Blueprint
- Assessed outcome scope: LO-1; LO-2
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Final grade | Correct answer | Apply | Problem | independent | 10 | 10 | none identified | review |
- Evidence level claimed: formally validated
"""
        result = run_script(
            "validate_assessment_blueprint.py",
            content,
            ".md",
            "--required-outcome",
            "LO-2",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Required outcome is not sampled: LO-2", result.stdout)
        self.assertIn("Formal-validation claim requires", result.stdout)

    def test_retired_alignment_outcome_is_not_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            alignment = directory / "alignment-map.md"
            blueprint = directory / "assessment-blueprint.md"
            alignment.write_text(
                """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Analyze evidence | analyze | Analysis | deliberate practice | Cases | Rubric | approved |
| LO-2 | Defend a design | evaluate | Defense | feedback | Studio | Checklist | retired |
""",
                encoding="utf-8",
            )
            blueprint.write_text(
                """- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Judge analysis | Applies criteria | analyze | essay | independent | 20 | 10 | writing load | approved |
""",
                encoding="utf-8",
            )
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(alignment),
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_retired_item_does_not_satisfy_required_outcome(self) -> None:
        content = """- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| OLD-1 | LO-1 | Historical only | Student analyzes | analyze | essay | independent | 20 | 10 | none | retired |
"""
        result = run_script(
            "validate_assessment_blueprint.py",
            content,
            ".md",
            "--required-outcome",
            "LO-1",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Required outcome is not sampled: LO-1", result.stdout)
        self.assertIn("Assessment blueprint contains no active items", result.stdout)

    def test_unknown_status_evidence_dependency_cycle_and_infinity_are_rejected(
        self,
    ) -> None:
        content = """- Assessed outcome scope: LO-1
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Claim | Apply | Response | A-2 | inf | 2 | none | done |
| A-2 | LO-1 | Feedback | Claim | Apply | Response | A-1 | 2 | 2 | none | review |
- Evidence level claimed: unquestionably-valid
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "unknown status done",
            "expected time must be a positive number",
            "Circular item dependencies",
            "Unknown evidence level claimed",
        ):
            self.assertIn(expected, result.stdout)

    def test_item_outside_explicit_scope_is_rejected(self) -> None:
        content = """- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-2 | Feedback | Explains reasoning | understand | essay | independent | 10 | 5 | none identified | approved |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "Assessment item uses outcome outside declared scope: LO-2", result.stdout
        )
        self.assertIn("Required outcome is not sampled: LO-1", result.stdout)

    def test_missing_assessed_outcome_scope_is_rejected(self) -> None:
        content = """- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Explains reasoning | understand | essay | independent | 10 | 5 | none identified | approved |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Missing assessed outcome scope", result.stdout)

    def test_scope_must_reference_an_active_alignment_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            alignment = directory / "alignment-map.md"
            blueprint = directory / "assessment-blueprint.md"
            alignment.write_text(
                """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain | understand | Explanation | retrieval | Activity | Feedback | approved |
| LO-2 | Defend | evaluate | Defense | feedback | Studio | Rubric | retired |
""",
                encoding="utf-8",
            )
            blueprint.write_text(
                """- Assessed outcome scope: LO-2
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-2 | Feedback | Defends design | evaluate | oral defense | independent | 10 | 5 | none identified | approved |
""",
                encoding="utf-8",
            )
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(alignment),
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "Assessed outcome scope is not active in the alignment map: LO-2",
            result.stdout,
        )

    def test_all_active_scope_rejects_an_alignment_with_no_active_outcomes(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            alignment = directory / "alignment-map.md"
            blueprint = directory / "assessment-blueprint.md"
            alignment.write_text(
                """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain | understand | Explanation | retrieval | Archived activity | Archived feedback | retired |
""",
                encoding="utf-8",
            )
            blueprint.write_text(
                """- Assessed outcome scope: all-active
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Explains reasoning | understand | essay | independent | 10 | 5 | none identified | approved |
""",
                encoding="utf-8",
            )
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(alignment),
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "Assessed outcome scope all-active contains no active aligned outcomes",
            result.stdout,
        )
        self.assertIn(
            "Assessment item uses outcome outside declared scope: LO-1", result.stdout
        )

    def _demand_pair(
        self, directory: Path, outcome_demand: str, item_demands: tuple[str, ...]
    ) -> Path:
        alignment = directory / "alignment-map.md"
        blueprint = directory / "assessment-blueprint.md"
        alignment.write_text(
            "| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning "
            "| Learning mechanism | Learning activity/support | Feedback or assessment | Status |\n"
            "|---|---|---|---|---|---|---|---|\n"
            f"| LO-1 | Decide under uncertainty | {outcome_demand} | Recommendation | contrasting cases "
            "| Comparison | Rubric | approved |\n",
            encoding="utf-8",
        )
        rows = "\n".join(
            f"| A-{index} | LO-1 | Use | Claim | {demand} | essay | independent | 10 | 5 | none identified | approved |"
            for index, demand in enumerate(item_demands, start=1)
        )
        blueprint.write_text(
            "- Assessed outcome scope: LO-1\n- Evidence level claimed: classroom-reviewed\n\n"
            "| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand "
            "| Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|\n" + rows + "\n",
            encoding="utf-8",
        )
        return blueprint

    def test_assessment_below_outcome_demand_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            blueprint = self._demand_pair(directory, "evaluate", ("apply",))
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(directory / "alignment-map.md"),
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "LO-1: highest active item demand apply is below the aligned outcome demand evaluate",
            result.stdout,
        )

    def test_scaffolding_item_below_outcome_demand_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            blueprint = self._demand_pair(directory, "evaluate", ("apply", "evaluate"))
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(directory / "alignment-map.md"),
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_demand_match_is_skipped_without_an_alignment_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            blueprint = self._demand_pair(directory, "evaluate", ("apply",))
            result = run_path("validate_assessment_blueprint.py", blueprint)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_item_cognitive_demand_is_reported(self) -> None:
        content = """- Assessed outcome scope: LO-1
- Evidence level claimed: classroom-reviewed

| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Explanation | synthesize | essay | independent | 10 | 5 | none identified | approved |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown cognitive demand synthesize", result.stdout)

    def test_zero_point_formative_item_is_allowed(self) -> None:
        content = """# Assessment Blueprint
- Assessed outcome scope: LO-1
- Evidence level claimed: classroom-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Formative feedback | Explanation | understand | response | independent | 5 | 0 | none identified | approved |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_separator_only_item_id_is_reported_without_a_traceback(self) -> None:
        content = """# Assessment Blueprint
- Assessed outcome scope: LO-1
- Evidence level claimed: classroom-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| ; | LO-1 | Feedback | Explanation | understand | response | independent | 5 | 0 | none identified | approved |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("identifier list contains no identifiers", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_markdown_assessment_metadata_is_structural_error(self) -> None:
        base = """- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Explanation | understand | essay | independent | 10 | 5 | none identified | approved |
"""
        cases = (
            (
                base.replace(
                    "- Evidence level claimed: expert-reviewed",
                    "- Evidence level claimed: expert-reviewed\n"
                    "- Evidence level claimed: formally-validated",
                ),
                "duplicate evidence-level claims",
            ),
            (
                base.replace(
                    "- Assessed outcome scope: LO-1",
                    "- Assessed outcome scope: LO-1\n" "- Assessed outcome scope: LO-2",
                ),
                "duplicate assessed-outcome scopes",
            ),
        )
        for content, expected in cases:
            with self.subTest(expected=expected):
                result = run_script("validate_assessment_blueprint.py", content)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout)

    def test_unknown_alignment_status_does_not_define_active_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            alignment = directory / "alignment-map.md"
            blueprint = directory / "assessment-blueprint.md"
            alignment.write_text(
                """| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain | understand | Explanation | retrieval | Activity | Feedback | done |
""",
                encoding="utf-8",
            )
            blueprint.write_text(
                """- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Feedback | Explanation | understand | essay | independent | 10 | 5 | none identified | approved |
""",
                encoding="utf-8",
            )
            result = run_path(
                "validate_assessment_blueprint.py",
                blueprint,
                "--alignment-map",
                str(alignment),
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "Assessed outcome scope is not active in the alignment map: LO-1",
            result.stdout,
        )


class CourseCurriculumMapValidatorTests(unittest.TestCase):
    def test_coherent_course_map_passes(self) -> None:
        content = """# Course Curriculum Map
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | external: prerequisite course | Prediction and model sketch | Diagnostic feedback | 2 | approved |
| 2 | 2 | LO-1 | practice | none | Contrasting cases | Peer and instructor feedback | 3 | approved |
| 3 | 3 | LO-1 | assess | none | Novel transfer problem | Scored rubric | 2 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--max-hours-per-module",
            "8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    MASSED_PRACTICE_MAP = """# Course Curriculum Map
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | LO-1 | introduce | none | Prediction | Diagnostic feedback | 2 | approved |
| 2 | 2 | LO-1 | practice | none | Problem set | Peer feedback | 2 | approved |
| 3 | 2 | LO-1 | practice | none | Problem set | Instructor feedback | 2 | approved |
| 4 | 6 | LO-1 | assess | none | Novel transfer problem | Scored rubric | 2 | approved |
"""

    def test_massed_practice_is_silent_without_the_flag(self) -> None:
        result = run_script(
            "validate_course_curriculum_map.py", self.MASSED_PRACTICE_MAP
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_massed_practice_is_reported_with_the_flag(self) -> None:
        result = run_script(
            "validate_course_curriculum_map.py",
            self.MASSED_PRACTICE_MAP,
            ".md",
            "--check-practice-distribution",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("practice occurrences are massed in module/week 2", result.stdout)

    def test_distributed_practice_passes_the_flag(self) -> None:
        content = self.MASSED_PRACTICE_MAP.replace(
            "| 3 | 2 | LO-1 | practice", "| 3 | 4 | LO-1 | practice"
        )
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--check-practice-distribution",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blank_module_does_not_produce_a_massed_practice_claim(self) -> None:
        content = """# Course Curriculum Map
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | none | Prediction | Diagnostic | 1 | approved |
| 2 |  | LO-1 | practice | none | Problem set | Peer feedback | 1 | approved |
| 3 |  | LO-1 | practice | none | Problem set | Instructor feedback | 1 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--check-practice-distribution",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing module/week", result.stdout)
        self.assertNotIn("massed", result.stdout)

    def test_single_practice_row_is_not_flagged_as_massed(self) -> None:
        content = """# Course Curriculum Map
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | none | Prediction | Diagnostic feedback | 2 | approved |
| 2 | 2 | LO-1 | practice | none | Problem set | Peer feedback | 2 | approved |
| 3 | 3 | LO-1 | assess | none | Transfer problem | Scored rubric | 2 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--check-practice-distribution",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_course_map_detects_sequence_cycle_and_overload(self) -> None:
        content = """# Course Curriculum Map
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | assess | LO-2 | Final design | Scored rubric | 6 | review |
| 1 | 1 | LO-2 | introduce | LO-1 | Initial model | Diagnostic feedback | 5 | review |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--max-hours-per-module",
            "8",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("before introduction or a declared external prior", result.stdout)
        self.assertIn("mastery/assessment appears before practice", result.stdout)
        self.assertIn("Circular outcome prerequisites", result.stdout)
        self.assertIn("exceeds limit 8", result.stdout)

    def test_sequence_is_evaluated_independently_of_physical_row_order(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 3 | 3 | LO-1 | assess | none | Transfer task | Rubric | 2 | approved |
| 1 | 1 | LO-1 | introduce | none | Initial model | Feedback | 2 | approved |
| 2 | 2 | LO-1 | practice | none | Cases | Feedback | 2 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_same_sequence_does_not_create_false_prior_development(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | none | Initial model | Feedback | 2 | review |
| 1 | 1 | LO-1 | assess | none | Transfer task | Rubric | 2 | review |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("before introduction or a declared external prior", result.stdout)
        self.assertIn("mastery/assessment appears before practice", result.stdout)

    def test_practice_after_assessment_does_not_satisfy_progression(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | none | Initial model | Feedback | 2 | approved |
| 2 | 2 | LO-1 | assess | none | Transfer task | Rubric | 2 | approved |
| 3 | 3 | LO-1 | practice | none | Cases | Feedback | 2 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--require-complete-progression",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("mastery/assessment appears before practice", result.stdout)

    def test_mixed_external_and_internal_prerequisites_are_checked(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | external: calculus; LO-9 | Initial model | Feedback | 2 | review |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown prerequisite outcome lo-9", result.stdout)

    def test_comma_separated_prerequisites_are_rejected_with_separator_help(
        self,
    ) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-3 | introduce | LO-1, LO-2 | Initial model | Feedback | 2 | review |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("use semicolons between identifiers", result.stdout)

    def test_external_prerequisite_description_preserves_a_comma(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | external: OSHA standard, 2024 edition | Initial model | Feedback | 2 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_prerequisite_must_be_developed_before_dependent_outcome(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-2 | introduce | LO-1 | Dependent activity | Feedback | 2 | approved |
| 2 | 2 | LO-1 | introduce | none | Prerequisite activity | Feedback | 2 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "prerequisite outcome lo-1 has no earlier development or declared external prior",
            result.stdout,
        )

    def test_earlier_prerequisite_development_passes(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | none | Prerequisite activity | Feedback | 2 | approved |
| 2 | 2 | LO-2 | introduce | LO-1 | Dependent activity | Feedback | 2 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_separator_only_curriculum_outcome_is_reported_without_a_traceback(
        self,
    ) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | ; | introduce | none | Activity | Feedback | 2 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("identifier list contains no identifiers", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_handoff_progression_requires_practice_and_terminal_evidence(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Week 1 | LO-1 | introduce | external: entry knowledge | Guided example | Minute paper | 1 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--require-complete-progression",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("complete progression is missing practice", result.stdout)
        self.assertIn(
            "complete progression is missing mastery or assessment", result.stdout
        )

    def test_retired_rows_do_not_count_toward_current_workload(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Old module | LO-1 | introduce | external: prior | Archived activity | Archived feedback | 99 | retired |
| 2 | Current module | LO-2 | introduce | external: prior | Current activity | Feedback | 2 | approved |
"""
        result = run_script(
            "validate_course_curriculum_map.py",
            content,
            ".md",
            "--max-hours-per-module",
            "8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_retired_rows_do_not_shift_reported_row_numbers(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Old module | LO-1 | introduce | external: prior | Archived activity | Archived feedback | 99 | retired |
| 2 | Current module | LO-2 | introduce | external: prior | Current activity | Feedback | invalid | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Row 2 (LO-2): workload must be a positive number", result.stdout)

    def test_retired_only_map_reports_no_active_rows(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Old module | LO-1 | introduce | external: prior | Archived activity | Archived feedback | 2 | retired |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Course curriculum map contains no active rows", result.stdout)

    def test_malformed_retired_row_is_still_validated_structurally(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  | retired |
| 1 | Week 1 | LO-1 | introduce | external: prior | Activity | Feedback | 1 | approved |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Row 1: missing outcome ID", result.stdout)
        self.assertIn("missing sequence", result.stdout)


class ValidatorFixtureAndCliTests(unittest.TestCase):
    CASES = (
        ("validate_design_state.py", "design_state", (), 0, 2, 1, 0),
        ("validate_alignment_map.py", "alignment", (), 0, 2, 1, 0),
        ("validate_artifact_manifest.py", "artifact_manifest", (), 0, 2, 1, 0),
        (
            "validate_assessment_blueprint.py",
            "assessment_blueprint",
            ("--required-outcome", "LO-9"),
            0,
            2,
            1,
            0,
        ),
        (
            "validate_course_curriculum_map.py",
            "course_curriculum_map",
            ("--max-hours-per-module", "8"),
            0,
            2,
            1,
            0,
        ),
    )

    def test_valid_invalid_malformed_and_boundary_fixtures(self) -> None:
        for (
            script,
            fixture_dir,
            invalid_args,
            valid_code,
            invalid_code,
            malformed_code,
            boundary_code,
        ) in self.CASES:
            with self.subTest(script=script, fixture="valid"):
                result = run_path(script, FIXTURES / fixture_dir / "valid.md")
                self.assertEqual(
                    result.returncode, valid_code, result.stdout + result.stderr
                )
            with self.subTest(script=script, fixture="invalid"):
                result = run_path(
                    script, FIXTURES / fixture_dir / "invalid.md", *invalid_args
                )
                self.assertEqual(
                    result.returncode, invalid_code, result.stdout + result.stderr
                )
            with self.subTest(script=script, fixture="malformed"):
                result = run_path(script, FIXTURES / fixture_dir / "malformed.md")
                self.assertEqual(
                    result.returncode, malformed_code, result.stdout + result.stderr
                )
            boundary_path = next((FIXTURES / fixture_dir).glob("boundary.*"))
            with self.subTest(script=script, fixture="boundary"):
                result = run_path(script, boundary_path)
                self.assertEqual(
                    result.returncode, boundary_code, result.stdout + result.stderr
                )

    def test_missing_file_returns_structural_error_for_every_validator(self) -> None:
        missing = FIXTURES / "does-not-exist.md"
        for script, *_ in self.CASES:
            with self.subTest(script=script):
                result = run_path(script, missing)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("ERROR:", result.stdout)

    def test_help_includes_usage_and_examples_for_every_validator(self) -> None:
        for script, *_ in self.CASES:
            with self.subTest(script=script):
                result = run_help(script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("usage:", result.stdout.lower())
                self.assertIn("Example", result.stdout)

    def test_assessment_fixture_exercises_quality_rules(self) -> None:
        result = run_path(
            "validate_assessment_blueprint.py",
            FIXTURES / "assessment_blueprint" / "invalid.md",
            "--required-outcome",
            "LO-9",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "duplicate item ID A-1",
            "expected time must be a positive number",
            "points must be a nonnegative finite number",
            "assessment content has no item ID",
            "Required outcome is not sampled: LO-9",
            "Formal-validation claim requires",
        ):
            self.assertIn(expected, result.stdout)

    def test_assessment_empty_row_rule(self) -> None:
        content = """| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
"""
        result = run_script("validate_assessment_blueprint.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("empty row", result.stdout)

    def test_course_map_fixture_exercises_coherence_rules(self) -> None:
        result = run_path(
            "validate_course_curriculum_map.py",
            FIXTURES / "course_curriculum_map" / "invalid.md",
            "--max-hours-per-module",
            "8",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "before introduction or a declared external prior",
            "mastery/assessment appears before practice",
            "missing feedback/assessment",
            "invalid stage launch",
            "unknown prerequisite outcome lo-9",
            "Circular outcome prerequisites",
            "workload must be a positive number",
            "exceeds limit 8",
        ):
            self.assertIn(expected, result.stdout)

    def test_course_map_missing_outcome_id_rule(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 |  | introduce | none | Activity | Feedback | 1 | draft |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing outcome ID", result.stdout)

    def test_table_validators_report_empty_data_sets(self) -> None:
        empty_cases = (
            (
                "validate_alignment_map.py",
                "| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |\n|---|---|---|---|---|---|---|---|\n",
            ),
            (
                "validate_artifact_manifest.py",
                "| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
            ),
            (
                "validate_assessment_blueprint.py",
                "| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |\n|---|---|---|---|---|---|---|---|---|---|---|\n",
            ),
            (
                "validate_course_curriculum_map.py",
                "| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |\n|---|---|---|---|---|---|---|---|---|\n",
            ),
        )
        for script, content in empty_cases:
            with self.subTest(script=script):
                result = run_script(script, content)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


class ProjectValidatorTests(unittest.TestCase):
    BRIEF = """# Course Design Brief
- Schema version: 1.0
- Engagement tier: Project
## Course context
- Course or module: BIO 101
## Intended learning
- Learning outcomes: Explain a mechanism.
## Access, participation, and belonging
- Known access constraints without sensitive student details: None identified.
## Constraints
- Technology and format: Markdown.
## Implementation load
- Minimum viable fallback: Printable activity.
## Collaboration
- Interaction level: Co-design
- Requested artifacts: Student worksheet.
## Status
### Confirmed
- Outcome approved.
### Assumed
- Prior knowledge present.
### Open
- Accessibility review pending.
### Current phase
- Produce aligned artifacts.
### Next decision
- Review the worksheet.
"""
    ALIGNMENT = """# Alignment Map
- Schema version: 1.0
| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | understand | Explanation | contrasting cases | Comparison | Feedback | approved |
"""

    def test_minimal_indexed_project_passes(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF,
                "alignment-map.md": self.ALIGNMENT,
            }
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_project_detects_unknown_cross_file_outcome(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| artifact-manifest.md | artifact authority | course owner | 1.0 | review | 2026-08-01 | current |
"""
        manifest = """# Artifact Manifest
- Schema version: 1.0
| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-9 | draft | manual | none | 2026-08-01 | https://example.edu/plan | https://example.edu/access | not required |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF,
                "alignment-map.md": self.ALIGNMENT,
                "artifact-manifest.md": manifest,
            }
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outcome is not defined in alignment-map.md: lo-9", result.stdout)

    def test_project_requires_active_index_paths(self) -> None:
        index = """- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| missing.md | state | course owner | 1.0 | draft | 2026-08-01 | current |
"""
        result = run_project({"project-index.md": index})
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("active state file does not exist", result.stdout)

    def test_project_rejects_duplicate_resolved_state_file_aliases(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| ./course-design-brief.md | duplicate alias | course owner | 1.0 | approved | 2026-08-01 | duplicate |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF,
            },
            "--design-profile",
            "establish",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("resolves to the same target as row 1", result.stdout)

    def test_empty_handoff_index_is_rejected(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
"""
        result = run_project({"project-index.md": index}, "--design-profile", "handoff")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("contains no state-file rows", result.stdout)
        self.assertIn("handoff profile requires", result.stdout)

    def test_project_requires_one_development_schema(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 2.0 | approved | 2026-08-01 | current |
"""
        other_schema_brief = self.BRIEF.replace(
            "Schema version: 1.0", "Schema version: 2.0"
        )
        result = run_project(
            {"project-index.md": index, "course-design-brief.md": other_schema_brief},
            "--design-profile",
            "establish",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "does not match project-index.md development schema", result.stdout
        )

    def test_project_requires_matching_state_dates(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Last updated: 2026-08-01
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
"""
        brief = self.BRIEF.replace(
            "- Schema version: 1.0",
            "- Schema version: 1.0\n- Last updated: 2026-07-31",
        )
        result = run_project(
            {"project-index.md": index, "course-design-brief.md": brief},
            "--design-profile",
            "establish",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "last updated 2026-07-31 does not match index 2026-08-01", result.stdout
        )

    def test_project_requires_index_and_state_dates(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Last updated:
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
"""
        brief = self.BRIEF.replace(
            "- Schema version: 1.0",
            "- Schema version: 1.0\n- Last updated:",
        )
        result = run_project(
            {"project-index.md": index, "course-design-brief.md": brief},
            "--design-profile",
            "establish",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("project-index.md: missing last-updated date", result.stdout)
        self.assertIn(
            "course-design-brief.md: missing last-updated date", result.stdout
        )

    def test_project_passes_alignment_to_blueprint_coverage_check(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| assessment-blueprint.md | assessment authority | course owner | 1.0 | review | 2026-08-01 | current |
"""
        alignment = self.ALIGNMENT + (
            "| LO-2 | Defend a design | evaluate | Oral defense | feedback | Studio | Rubric | approved |\n"
        )
        blueprint = """# Assessment Blueprint
- Schema version: 1.0
- Assessed outcome scope: all-active
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Judge explanation | Explains mechanism | understand | essay | independent | 20 | 10 | writing load | approved |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF,
                "alignment-map.md": alignment,
                "assessment-blueprint.md": blueprint,
            }
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Required outcome is not sampled: LO-2", result.stdout)

    def test_project_respects_explicit_assessment_scope(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| assessment-blueprint.md | assessment authority | course owner | 1.0 | review | 2026-08-01 | current |
"""
        alignment = self.ALIGNMENT + (
            "| LO-2 | Defend a design | evaluate | Oral defense | feedback | Studio | Rubric | approved |\n"
        )
        blueprint = """# Assessment Blueprint
- Schema version: 1.0
- Assessed outcome scope: LO-1
- Evidence level claimed: expert-reviewed
| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-1 | LO-1 | Judge explanation | Explains mechanism | understand | essay | independent | 20 | 10 | writing load | approved |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF,
                "alignment-map.md": alignment,
                "assessment-blueprint.md": blueprint,
            }
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_course_tier_requires_curriculum_map_during_production(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Course
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF.replace(
                    "Engagement tier: Project", "Engagement tier: Course"
                ),
                "alignment-map.md": self.ALIGNMENT,
            }
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "requires an active project-index entry for course-curriculum-map.md",
            result.stdout,
        )

    def test_course_tier_map_covers_every_active_aligned_outcome(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Course
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| course-curriculum-map.md | course sequence | course owner | 1.0 | review | 2026-08-01 | current |
"""
        alignment = self.ALIGNMENT + (
            "| LO-2 | Defend a design | evaluate | Oral defense | feedback | Studio | Rubric | approved |\n"
        )
        course_map = """# Course Curriculum Map
- Schema version: 1.0
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Week 1 | LO-1 | introduce | external: prior course | Guided model | Feedback | 2 | approved |
"""
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": self.BRIEF.replace(
                    "Engagement tier: Project", "Engagement tier: Course"
                ),
                "alignment-map.md": alignment,
                "course-curriculum-map.md": course_map,
            }
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "active aligned outcome is not mapped for the Course tier: lo-2",
            result.stdout,
        )

    def test_project_rejects_state_path_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "project"
            external = root / "external"
            project.mkdir()
            external.mkdir()
            (external / "course-design-brief.md").write_text(
                self.BRIEF, encoding="utf-8"
            )
            (project / "project-index.md").write_text(
                """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| ../external/course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | external |
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_project.py"),
                    str(project),
                    "--design-profile",
                    "establish",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "state file resolves outside the project directory", result.stdout
        )

    def test_project_rejects_symlinked_index_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project = root / "project"
            project.mkdir()
            external_index = root / "external-project-index.md"
            external_index.write_text(
                """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
""",
                encoding="utf-8",
            )
            (project / "project-index.md").symlink_to(external_index)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_project.py"),
                    str(project),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "project-index.md resolves outside the project directory", result.stdout
        )

    def test_project_reports_an_unresolvable_index_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "project-index.md").symlink_to("project-index.md")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_project.py"),
                    str(project),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Cannot resolve project-index.md", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_project_reports_an_unresolvable_state_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "course-design-brief.md").symlink_to("course-design-brief.md")
            (project / "project-index.md").write_text(
                """# Project Index
- Schema version: 1.0
- Engagement tier: Project
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "validate_project.py"),
                    str(project),
                    "--design-profile",
                    "establish",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Cannot resolve state file course-design-brief.md", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_course_handoff_enforces_complete_progression(self) -> None:
        index = """# Project Index
- Schema version: 1.0
- Engagement tier: Course
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| course-curriculum-map.md | course sequence | course owner | 1.0 | review | 2026-08-01 | current |
| artifact-manifest.md | artifact authority | course owner | 1.0 | review | 2026-08-01 | current |
| design-log.md | decisions | course owner | 1.0 | approved | 2026-08-01 | current |
| source-register.md | provenance | course owner | 1.0 | approved | 2026-08-01 | current |
| capability-manifest.md | capabilities | course owner | 1.0 | approved | 2026-08-01 | current |
"""
        brief = self.BRIEF.replace(
            "Engagement tier: Project", "Engagement tier: Course"
        ).replace(
            "- Known access constraints without sensitive student details: None identified.",
            "- Known access constraints without sensitive student details: None identified.\n"
            "- Accessibility contact, review, procurement, or exception process: Accessibility office.",
        )
        course_map = """# Course Curriculum Map
- Schema version: 1.0
| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Week 1 | LO-1 | introduce | external: prior course | Guided model | Feedback | 2 | approved |
"""
        manifest = """# Artifact Manifest
- Schema version: 1.0
| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown |  |  |  | https://example.edu/ws | student | LO-1 | draft | manual | none | 2026-08-01 | not required | pending | not required |
"""
        state_stub = "# State\n- Schema version: 1.0\n"
        result = run_project(
            {
                "project-index.md": index,
                "course-design-brief.md": brief,
                "alignment-map.md": self.ALIGNMENT,
                "course-curriculum-map.md": course_map,
                "artifact-manifest.md": manifest,
                "design-log.md": state_stub,
                "source-register.md": state_stub,
                "capability-manifest.md": state_stub,
            },
            "--design-profile",
            "handoff",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("complete progression is missing practice", result.stdout)
        self.assertIn(
            "complete progression is missing mastery or assessment", result.stdout
        )

    def test_missing_project_directory_is_structural_error(self) -> None:
        result = run_path("validate_project.py", FIXTURES / "does-not-exist")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Project directory does not exist", result.stdout)

    def test_project_help_includes_usage_and_examples(self) -> None:
        result = run_help("validate_project.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("usage:", result.stdout.lower())
        self.assertIn("Examples", result.stdout)


class RepositoryIntegrityTests(unittest.TestCase):
    def test_repository_links_and_package_inventory_pass(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "check_repository.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inventory_drift_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = Path(temp_dir) / "inventory.txt"
            inventory.write_text(
                "course-development-partner/SKILL.md\n", encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tests" / "check_repository.py"),
                    "--inventory",
                    str(inventory),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unrecorded file", result.stdout)

    def test_missing_inventory_returns_one(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tests" / "check_repository.py"),
                "--inventory",
                "tests/does-not-exist.txt",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stdout)

    def test_privacy_screen_passes_with_bounded_claim(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tests" / "audit_privacy.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("human review still required", result.stdout)

    def test_forward_record_hashes_match_current_inputs(self) -> None:
        record = json.loads(
            (ROOT / "tests" / "remediation-forward-test-results.json").read_text(
                encoding="utf-8"
            )
        )
        scenario_hash = hashlib.sha256(
            (ROOT / "tests" / "faculty-review-scenarios.md").read_bytes()
        ).hexdigest()
        rubric_hash = hashlib.sha256(
            (ROOT / "tests" / "evaluator-rubric.md").read_bytes()
        ).hexdigest()
        self.assertEqual(record["current_scenario_file_sha256"], scenario_hash)
        self.assertEqual(record["current_rubric_file_sha256"], rubric_hash)
        self.assertEqual(record["evidence_status"], "historical-exploratory-only")


class PackageContentTests(unittest.TestCase):
    def test_every_reference_is_routed_from_skill(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        for reference in sorted((skill_root / "references").glob("*.md")):
            self.assertIn(f"references/{reference.name}", skill_text, reference.name)

    def test_development_docs_are_outside_runtime_package(self) -> None:
        skill_root = ROOT / "course-development-partner"
        self.assertFalse((skill_root / "README.md").exists())
        self.assertFalse((skill_root / "design.md").exists())
        self.assertFalse((skill_root / "TODO.md").exists())

    def test_accessibility_routing_is_operational_and_bounded(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        reference_text = (
            skill_root / "references" / "accessibility-and-compliance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("assets/accessibility-review.md", skill_text)
        self.assertIn("WCAG 2.1", reference_text)
        self.assertIn("WCAG 2.1 Level AA", reference_text)
        self.assertIn("Title II web/mobile rule applies", reference_text)
        self.assertIn("WCAG 2.2", reference_text)
        self.assertIn("WCAG2ICT", reference_text)
        self.assertIn(
            "must not make a legal or institutional compliance determination",
            (skill_root / "assets" / "accessibility-review.md").read_text(
                encoding="utf-8"
            ),
        )

    def test_visual_guidance_offers_optional_neutral_palette(self) -> None:
        skill_root = ROOT / "course-development-partner"
        visual_text = (skill_root / "references" / "visual-design.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("neutral example palette", visual_text)
        self.assertIn("Primary dark", visual_text)
        self.assertIn("Primary accent", visual_text)
        self.assertIn("#CFB991", visual_text)
        self.assertIn("#DAAA00", visual_text)
        self.assertIn("optional", visual_text.lower())
        self.assertIn("unbranded", visual_text.lower())

    def test_auto_mode_is_noninteractive_but_preserves_authority(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        interaction_text = (
            skill_root / "references" / "interaction-protocol.md"
        ).read_text(encoding="utf-8")
        brief_text = (skill_root / "assets" / "course-design-brief.md").read_text(
            encoding="utf-8"
        )
        metadata_text = (skill_root / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        artifact_text = (skill_root / "references" / "artifact-patterns.md").read_text(
            encoding="utf-8"
        )
        rich_text = (
            skill_root / "references" / "rich-artifact-production.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Auto mode", skill_text)
        self.assertIn("does not ask the educator", skill_text)
        self.assertIn("do not execute the side effect", interaction_text)
        self.assertIn("Do not end Auto output with a request", interaction_text)
        self.assertIn("Co-design | Guided | Rapid | Auto", brief_text)
        self.assertNotIn("Goal", brief_text)
        self.assertIn("Rapid and Auto are not aliases", interaction_text)
        self.assertIn("one final faculty review", interaction_text)
        self.assertIn("design, review, validate, or produce", metadata_text)
        self.assertIn(
            "Rubric calibration with authentic student responses is always interactive",
            skill_text,
        )
        self.assertIn("use Co-design or Guided mode", interaction_text)
        self.assertIn("In Auto mode", artifact_text)
        self.assertIn("In Auto mode", rich_text)
        self.assertIn("without an approval checkpoint", rich_text)

    def test_cognitive_demand_vocabulary_is_documented_where_it_is_used(self) -> None:
        skill_root = ROOT / "course-development-partner"
        contract_text = (skill_root / "references" / "state-contract.md").read_text(
            encoding="utf-8"
        )
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        for token in (
            "remember",
            "understand",
            "apply",
            "analyze",
            "evaluate",
            "create",
        ):
            self.assertIn(token, contract_text, token)
            self.assertIn(token, skill_text, token)
        for asset in ("alignment-map.md", "assessment-blueprint.md"):
            asset_text = (skill_root / "assets" / asset).read_text(encoding="utf-8")
            self.assertIn("Cognitive demand values", asset_text, asset)

    def test_distributed_and_interleaved_practice_are_routed(self) -> None:
        skill_root = ROOT / "course-development-partner"
        evidence_text = (
            skill_root / "references" / "evidence-informed-design.md"
        ).read_text(encoding="utf-8")
        coherence_text = (
            skill_root / "references" / "course-coherence-and-implementation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Distributed practice", evidence_text)
        self.assertIn("Interleaving", evidence_text)
        self.assertIn("depress", evidence_text)
        self.assertIn("--check-practice-distribution", coherence_text)

    def test_motivation_and_team_design_are_present(self) -> None:
        evidence_text = (
            ROOT
            / "course-development-partner"
            / "references"
            / "evidence-informed-design.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "self-efficacy",
            "belonging",
            "Form teams deliberately",
            "Separate individual and team evidence",
        ):
            self.assertIn(expected, evidence_text, expected)
        self.assertIn("Never infer identity", evidence_text)
        self.assertIn("do not request sensitive identity data", evidence_text)

    def test_stem_authenticity_covers_profiles_and_safety_blocker(self) -> None:
        skill_root = ROOT / "course-development-partner"
        text = (skill_root / "references" / "stem-authenticity.md").read_text(
            encoding="utf-8"
        )
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertFalse(
            (skill_root / "references" / "engineering-authenticity.md").exists()
        )
        self.assertIn("references/stem-authenticity.md", skill_text)
        for profile in (
            "Engineering and engineering technology",
            "Computing and data disciplines",
            "Laboratory and experimental sciences",
            "Mathematics and quantitative reasoning",
        ):
            self.assertIn(profile, text, profile)
        self.assertIn("release blocker", text)
        self.assertIn("Auto mode may prepare the draft", text)
        self.assertIn(
            "never clears a safety blocker",
            (skill_root / "references" / "interaction-protocol.md").read_text(
                encoding="utf-8"
            ),
        )

    def test_grading_boundary_and_peer_evaluation_are_bounded(self) -> None:
        skill_root = ROOT / "course-development-partner"
        text = (skill_root / "references" / "assessment-quality.md").read_text(
            encoding="utf-8"
        )
        artifact_text = (skill_root / "references" / "artifact-patterns.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Know the grading-system boundary", text)
        self.assertIn("Use peer evaluation carefully", text)
        self.assertIn("not an automatic grade transformation", text)
        self.assertNotIn("Balanced — recommended", artifact_text)

    def test_section_references_resolve(self) -> None:
        """Every '§N' must name a real section, in this file or in the file it cites."""
        reference_dir = ROOT / "course-development-partner" / "references"
        sections = {
            path.name: {
                int(match)
                for match in re.findall(
                    r"^##\s+(\d+)\.\s",
                    path.read_text(encoding="utf-8"),
                    flags=re.MULTILINE,
                )
            }
            for path in reference_dir.glob("*.md")
        }
        checked = 0
        for name in sorted(sections):
            for line_number, line in enumerate(
                (reference_dir / name).read_text(encoding="utf-8").splitlines(), start=1
            ):
                for match in re.finditer(r"§(\d+)", line):
                    # A '§N' belongs to the last references/<file>.md named before it on the
                    # same line; with no such file it points at the current document.
                    preceding = re.findall(
                        r"references/([A-Za-z0-9._-]+\.md)", line[: match.start()]
                    )
                    target = preceding[-1] if preceding else name
                    self.assertIn(
                        target,
                        sections,
                        f"{name}:{line_number} cites unknown file {target}",
                    )
                    self.assertIn(
                        int(match.group(1)),
                        sections[target],
                        f"{name}:{line_number} cites §{match.group(1)} of {target}, "
                        "which has no such section",
                    )
                    checked += 1
        self.assertGreater(checked, 0, "no section references found to verify")

    def test_safety_review_asset_is_routed_and_blocking(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("assets/safety-review.md", skill_text)
        asset = (skill_root / "assets" / "safety-review.md").read_text(encoding="utf-8")
        self.assertIn("Responsible safety owner", asset)
        self.assertIn("Authoritative source and date", asset)
        self.assertIn("must not make one", asset)
        manifest = (skill_root / "assets" / "artifact-manifest.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Safety review", manifest)

    def test_brief_records_the_new_intake_answers(self) -> None:
        brief = (
            ROOT / "course-development-partner" / "assets" / "course-design-brief.md"
        ).read_text(encoding="utf-8")
        for field in (
            "How scores combine into a course grade",
            "Revision, resubmission, retake, or replacement policy",
            "Team formation basis and rationale",
            "How team and individual performance each reach the grade",
            "Responsible safety owner and role",
            "TA or grader disciplinary preparation, calibration, and decision authority",
        ):
            self.assertIn(field, brief, field)

    def test_demand_check_limits_are_stated(self) -> None:
        contract = (
            ROOT / "course-development-partner" / "references" / "state-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn("not difficulty", contract)
        self.assertIn("cannot substitute for reading the items", contract)

    def test_builtin_guidance_declares_its_own_evidence_basis(self) -> None:
        text = (
            ROOT
            / "course-development-partner"
            / "references"
            / "evidence-informed-design.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Apply that standard to this reference too", text)
        self.assertIn("synthesized practice guidance", text)

    def test_ta_preparation_and_class_size_are_routed(self) -> None:
        skill_root = ROOT / "course-development-partner"
        coherence = (
            skill_root / "references" / "course-coherence-and-implementation.md"
        ).read_text(encoding="utf-8")
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Prepare teaching assistants and graders", coherence)
        self.assertIn("Adjust the design to class size", coherence)
        self.assertIn("Decision authority", coherence)
        self.assertIn("teaching-assistant and grader preparation", skill_text)
        self.assertIn("program-outcome mapping across a degree", skill_text)

    def test_worked_example_tables_actually_validate(self) -> None:
        """The worked example claims specific validator outcomes; keep those claims true."""
        example = (
            ROOT / "course-development-partner" / "references" / "worked-example.md"
        )
        for script, args in (
            ("validate_alignment_map.py", ()),
            ("validate_course_curriculum_map.py", ("--check-practice-distribution",)),
            ("validate_assessment_blueprint.py", ("--alignment-map", str(example))),
        ):
            with self.subTest(script=script):
                result = run_path(script, example, *args)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_worked_example_is_routed_and_end_to_end(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/worked-example.md", skill_text)
        text = (skill_root / "references" / "worked-example.md").read_text(
            encoding="utf-8"
        )
        for stage in (
            "Establish what students already know",
            "Set the outcome and its evidence",
            "Place it in the course",
            "Blueprint the assessment",
            "Draft the rubric",
            "Validate",
        ):
            self.assertIn(stage, text, stage)

    def test_rich_artifact_contract_requires_evidence_and_fallback(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        reference_text = (
            skill_root / "references" / "rich-artifact-production.md"
        ).read_text(encoding="utf-8")
        plan_text = (skill_root / "assets" / "production-plan.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("assets/production-plan.md", skill_text)
        self.assertIn("editable source", reference_text)
        self.assertIn("rendered or playback inspection", reference_text)
        self.assertIn("Markdown or neutral-data fallback", plan_text)
        self.assertIn("Open/edit/reopen", plan_text)


if __name__ == "__main__":
    unittest.main()
