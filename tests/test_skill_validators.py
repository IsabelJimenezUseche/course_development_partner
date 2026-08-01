from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "course-development-partner" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"


def run_script(name: str, content: str, suffix: str = ".md", *args: str) -> subprocess.CompletedProcess[str]:
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
- Interaction level: Studio
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

    def test_incomplete_design_state_returns_two(self) -> None:
        template = (ROOT / "course-development-partner" / "assets" / "course-design-brief.md").read_text()
        result = run_script("validate_design_state.py", template)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_required_heading_at_wrong_level_is_structural_error(self) -> None:
        content = (FIXTURES / "design_state" / "valid.md").read_text(encoding="utf-8")
        content = content.replace("## Constraints", "### Constraints")
        result = run_script("validate_design_state.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Missing required level-2 heading: constraints", result.stdout)


class AlignmentValidatorTests(unittest.TestCase):
    def test_complete_alignment_passes(self) -> None:
        content = """# Alignment Map
| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | Explain | Annotated diagram | Comparison activity | Exit ticket | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_alignment_gap_returns_two(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|
| LO-1 | Explain a mechanism |  | Comparison activity | Exit ticket | draft |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing evidence of learning", result.stdout)

    def test_empty_and_unknown_statuses_are_both_rejected(self) -> None:
        result = run_path("validate_alignment_map.py", FIXTURES / "alignment" / "invalid.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing status", result.stdout)
        self.assertIn("unknown status done", result.stdout)
        self.assertIn("duplicate outcome ID LO-1", result.stdout)
        self.assertIn("activity or assessment has no outcome ID", result.stdout)

    def test_missing_alignment_fields_and_empty_row_are_reported(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|
| LO-1 |  |  |  |  |  |
|  |  |  |  |  |  |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for expected in (
            "missing observable learning outcome",
            "missing evidence of learning",
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

| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|
| LO-1 | Compare A \\| B | Explanation | Contrast cases | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_middle_row_is_structural_error(self) -> None:
        content = """| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|
| LO-1 | Explain | Evidence | Activity | Feedback | approved |
| LO-2 | This row is short | Evidence |
| LO-3 | Apply | Evidence | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Malformed Markdown table row", result.stdout)

    def test_duplicate_normalized_header_is_structural_error(self) -> None:
        content = """| Outcome ID | outcome   id | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|
| LO-1 | LO-1 | Explain | Evidence | Activity | Feedback | approved |
"""
        result = run_script("validate_alignment_map.py", content)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Duplicate normalized header", result.stdout)


class ArtifactManifestValidatorTests(unittest.TestCase):
    def test_teaching_ready_manifest_passes(self) -> None:
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws-1 | student | LO-1 | teaching-ready | technical; alignment; accessibility; reopen | none | 2026-07-31 | not required | https://example.edu/ws-1-accessibility |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_teaching_ready_with_blocker_returns_two(self) -> None:
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | worksheet.md | student | LO-1 | teaching-ready | technical; alignment; accessibility; reopen | solution not verified | 2026-07-31 | not required | accessibility-review.md |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unresolved blockers/open issues", result.stdout)

    def test_declared_pair_requires_labeled_student_and_instructor_variants(self) -> None:
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
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | missing.md | student | LO-1 | draft | manual | none | 2026-07-31 | https://example.edu/not-required | https://example.edu/pending |
"""
        result = run_script("validate_artifact_manifest.py", content, ".md", "--check-paths")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("local file or reference does not exist", result.stdout)

    def test_missing_fields_validation_evidence_and_family_context_are_reported(self) -> None:
        content = """| Artifact ID | Artifact family | Variant | Required variants | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  | student | student; instructor | markdown |  |  |  |  |  | none |  | not required | pending |
| A-2 |  |  |  | markdown | https://example.edu/a-2 | instructor | LO-1 | validated |  | none | 2026-07-31 | not required | pending |
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
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws | student | LO-1 | validated | none | none | 2026-13-40 | not required | pending |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown validation token none", result.stdout)
        self.assertIn("last reviewed must use YYYY-MM-DD", result.stdout)

    def test_calendar_invalid_iso_date_is_rejected(self) -> None:
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws | student | LO-1 | validated | technical; alignment | none | 2026-02-31 | not required | pending |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("last reviewed must use YYYY-MM-DD", result.stdout)

    def test_pending_non_file_evidence_is_not_treated_as_a_path_for_drafts(self) -> None:
        content = """| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws | student | LO-1 | draft | manual | none | 2026-08-01 | not applicable — plain Markdown | pending |
"""
        result = run_script("validate_artifact_manifest.py", content, ".md", "--check-paths")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_declared_variant_is_required(self) -> None:
        content = """| Artifact ID | Artifact family | Variant | Required variants | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | family-1 | student | student; instructor; solution | markdown | https://example.edu/student | student | LO-1 | draft | manual | none | 2026-07-31 | not required | pending |
| WS-2 | family-1 | instructor | student; instructor; solution | markdown | https://example.edu/instructor | instructor | LO-1 | draft | manual | none | 2026-07-31 | not required | pending |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("required solution variant is not represented", result.stdout)


class AssessmentBlueprintValidatorTests(unittest.TestCase):
    def test_complete_blueprint_passes(self) -> None:
        content = """# Assessment Blueprint
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

    def test_blueprint_detects_missing_coverage_and_overclaim(self) -> None:
        content = """# Assessment Blueprint
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

    def test_unknown_status_evidence_dependency_cycle_and_infinity_are_rejected(self) -> None:
        content = """| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
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
        self.assertIn("mastery/assessment appears before introduction or practice", result.stdout)
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
        self.assertIn("mastery/assessment appears before introduction or practice", result.stdout)

    def test_mixed_external_and_internal_prerequisites_are_checked(self) -> None:
        content = """| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | LO-1 | introduce | external: calculus; LO-9 | Initial model | Feedback | 2 | review |
"""
        result = run_script("validate_course_curriculum_map.py", content)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unknown prerequisite outcome lo-9", result.stdout)


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
        for script, fixture_dir, invalid_args, valid_code, invalid_code, malformed_code, boundary_code in self.CASES:
            with self.subTest(script=script, fixture="valid"):
                result = run_path(script, FIXTURES / fixture_dir / "valid.md")
                self.assertEqual(result.returncode, valid_code, result.stdout + result.stderr)
            with self.subTest(script=script, fixture="invalid"):
                result = run_path(script, FIXTURES / fixture_dir / "invalid.md", *invalid_args)
                self.assertEqual(result.returncode, invalid_code, result.stdout + result.stderr)
            with self.subTest(script=script, fixture="malformed"):
                result = run_path(script, FIXTURES / fixture_dir / "malformed.md")
                self.assertEqual(result.returncode, malformed_code, result.stdout + result.stderr)
            boundary_path = next((FIXTURES / fixture_dir).glob("boundary.*"))
            with self.subTest(script=script, fixture="boundary"):
                result = run_path(script, boundary_path)
                self.assertEqual(result.returncode, boundary_code, result.stdout + result.stderr)

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
            "points must be a positive number",
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
            "mastery/assessment appears before introduction or practice",
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
                "| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |\n|---|---|---|---|---|---|\n",
            ),
            (
                "validate_artifact_manifest.py",
                "| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |\n|---|---|---|---|---|---|---|---|---|---|---|\n",
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
- Interaction level: Studio
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
| Outcome ID | Observable learning outcome | Evidence of learning | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|
| LO-1 | Explain a mechanism | Explanation | Comparison | Feedback | approved |
"""

    def test_minimal_indexed_project_passes(self) -> None:
        index = """# Project Index
- Schema version: 1.0
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
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 1.0 | approved | 2026-08-01 | current |
| alignment-map.md | alignment authority | course owner | 1.0 | approved | 2026-08-01 | current |
| artifact-manifest.md | artifact authority | course owner | 1.0 | review | 2026-08-01 | current |
"""
        manifest = """# Artifact Manifest
- Schema version: 1.0
| Artifact ID | Artifact type | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review |
|---|---|---|---|---|---|---|---|---|---|---|
| WS-1 | markdown | https://example.edu/ws | student | LO-9 | draft | manual | none | 2026-08-01 | https://example.edu/plan | https://example.edu/access |
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
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| missing.md | state | course owner | 1.0 | draft | 2026-08-01 | current |
"""
        result = run_project({"project-index.md": index})
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("active state file does not exist", result.stdout)

    def test_empty_handoff_index_is_rejected(self) -> None:
        index = """# Project Index
- Schema version: 1.0
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
"""
        result = run_project(
            {"project-index.md": index}, "--design-profile", "handoff"
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("contains no state-file rows", result.stdout)
        self.assertIn("handoff profile requires", result.stdout)

    def test_project_requires_one_development_schema(self) -> None:
        index = """# Project Index
- Schema version: 1.0
| State file | Purpose | Authority/owner | Schema version | Status | Last updated | Notes |
|---|---|---|---|---|---|---|
| course-design-brief.md | design authority | course owner | 2.0 | approved | 2026-08-01 | current |
"""
        other_schema_brief = self.BRIEF.replace("Schema version: 1.0", "Schema version: 2.0")
        result = run_project(
            {"project-index.md": index, "course-design-brief.md": other_schema_brief},
            "--design-profile",
            "establish",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("does not match project-index.md development schema", result.stdout)

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
            inventory.write_text("course-development-partner/SKILL.md\n", encoding="utf-8")
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
        reference_text = (skill_root / "references" / "accessibility-and-compliance.md").read_text(encoding="utf-8")
        self.assertIn("assets/accessibility-review.md", skill_text)
        self.assertIn("WCAG 2.1", reference_text)
        self.assertIn("WCAG 2.1 Level AA", reference_text)
        self.assertIn("Title II web/mobile rule applies", reference_text)
        self.assertIn("WCAG 2.2", reference_text)
        self.assertIn("WCAG2ICT", reference_text)
        self.assertIn("must not make a legal or institutional compliance determination", (skill_root / "assets" / "accessibility-review.md").read_text(encoding="utf-8"))

    def test_visual_guidance_offers_optional_neutral_palette(self) -> None:
        skill_root = ROOT / "course-development-partner"
        visual_text = (skill_root / "references" / "visual-design.md").read_text(encoding="utf-8")
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
        interaction_text = (skill_root / "references" / "interaction-protocol.md").read_text(encoding="utf-8")
        brief_text = (skill_root / "assets" / "course-design-brief.md").read_text(encoding="utf-8")
        metadata_text = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("Auto mode", skill_text)
        self.assertIn("does not ask the educator", skill_text)
        self.assertIn("do not execute the side effect", interaction_text)
        self.assertIn("Do not end Auto output with a request", interaction_text)
        self.assertIn("Studio | Guided | Rapid | Auto", brief_text)
        self.assertNotIn("Goal", brief_text)
        self.assertIn("Rapid and Auto are not aliases", interaction_text)
        self.assertIn("one final faculty review", interaction_text)
        self.assertIn("available MCP or native tools", metadata_text)
        self.assertIn("Rubric calibration with authentic student responses is always interactive", skill_text)
        self.assertIn("use Studio or Guided mode", interaction_text)

    def test_rich_artifact_contract_requires_evidence_and_fallback(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        reference_text = (skill_root / "references" / "rich-artifact-production.md").read_text(encoding="utf-8")
        plan_text = (skill_root / "assets" / "production-plan.md").read_text(encoding="utf-8")
        self.assertIn("assets/production-plan.md", skill_text)
        self.assertIn("editable source", reference_text)
        self.assertIn("rendered or playback inspection", reference_text)
        self.assertIn("Markdown or neutral-data fallback", plan_text)
        self.assertIn("Open/edit/reopen", plan_text)


if __name__ == "__main__":
    unittest.main()
