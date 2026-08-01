from __future__ import annotations

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


class DesignStateValidatorTests(unittest.TestCase):
    def test_complete_design_state_passes(self) -> None:
        content = """# Course Design Brief
## Course context
- Course: BIO 101
## Intended learning
- Explain a mechanism
## Constraints
- Fifty minutes
## Collaboration
- Studio
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


class ArtifactManifestValidatorTests(unittest.TestCase):
    def test_teaching_ready_manifest_passes(self) -> None:
        content = """| Artifact ID | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed |
|---|---|---|---|---|---|---|---|
| WS-1 | https://example.edu/ws-1 | student | LO-1 | teaching-ready | technical; accessibility; rendering | none | 2026-07-31 |
"""
        result = run_script("validate_artifact_manifest.py", content)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_teaching_ready_with_blocker_returns_two(self) -> None:
        content = """| Artifact ID | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed |
|---|---|---|---|---|---|---|---|
| WS-1 | worksheet.md | student | LO-1 | teaching-ready | technical | solution not verified | 2026-07-31 |
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
        content = """| Artifact ID | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed |
|---|---|---|---|---|---|---|---|
| WS-1 | missing.md | student | LO-1 | draft | none | none | 2026-07-31 |
"""
        result = run_script("validate_artifact_manifest.py", content, ".md", "--check-paths")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("local reference does not exist", result.stdout)

    def test_missing_fields_validation_evidence_and_family_context_are_reported(self) -> None:
        content = """| Artifact ID | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  | student | student; instructor |  |  |  |  |  | none |  |
| A-2 |  |  |  | https://example.edu/a-2 | instructor | LO-1 | validated |  | none | 2026-07-31 |
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


class CourseCurriculumMapValidatorTests(unittest.TestCase):
    def test_coherent_course_map_passes(self) -> None:
        content = """# Course Curriculum Map
| Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|
| 1 | LO-1 | introduce | external: prerequisite course | Prediction and model sketch | Diagnostic feedback | 2 | approved |
| 2 | LO-1 | practice | none | Contrasting cases | Peer and instructor feedback | 3 | approved |
| 3 | LO-1 | assess | none | Novel transfer problem | Scored rubric | 2 | approved |
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
| Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|
| 1 | LO-1 | assess | LO-2 | Final design | Scored rubric | 6 | review |
| 1 | LO-2 | introduce | LO-1 | Initial model | Diagnostic feedback | 5 | review |
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
        content = """| Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|
| 1 |  | introduce | none | Activity | Feedback | 1 | draft |
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
                "| Artifact ID | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed |\n|---|---|---|---|---|---|---|---|\n",
            ),
            (
                "validate_assessment_blueprint.py",
                "| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |\n|---|---|---|---|---|---|---|---|---|---|---|\n",
            ),
            (
                "validate_course_curriculum_map.py",
                "| Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |\n|---|---|---|---|---|---|---|---|\n",
            ),
        )
        for script, content in empty_cases:
            with self.subTest(script=script):
                result = run_script(script, content)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


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

    def test_accessibility_profile_is_operational_and_bounded(self) -> None:
        skill_root = ROOT / "course-development-partner"
        skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        reference_text = (skill_root / "references" / "accessibility-and-compliance.md").read_text(encoding="utf-8")
        self.assertIn("assets/accessibility-review.md", skill_text)
        self.assertIn("WCAG 2.1 Level AA", reference_text)
        self.assertIn("Purdue University", reference_text)
        self.assertIn("must not make a legal or institutional compliance determination", (skill_root / "assets" / "accessibility-review.md").read_text(encoding="utf-8"))

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
