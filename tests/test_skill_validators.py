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


if __name__ == "__main__":
    unittest.main()
