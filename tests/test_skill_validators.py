from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "course-development-partner" / "scripts"


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


if __name__ == "__main__":
    unittest.main()
