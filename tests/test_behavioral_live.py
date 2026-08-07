"""Opt-in live behavioral test against an open-weight model.

Skipped unless RUN_LIVE_BEHAVIORAL=1, so the default suite stays hermetic.
Requires PURDUE_GENAI_* configuration in the environment or in the sibling
course_development_partner_app/.env (see run_behavioral_scenarios.py).

Heuristic passes are a screen, not qualifying forward-test evidence; the
retained transcript record is the input for human rubric application.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests" / "run_behavioral_scenarios.py"


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_BEHAVIORAL") == "1",
    "live behavioral run is opt-in: set RUN_LIVE_BEHAVIORAL=1",
)
class LiveBehavioralTests(unittest.TestCase):
    def test_partner_experience_scenarios_pass_heuristics(self) -> None:
        result = subprocess.run(
            [sys.executable, str(RUNNER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=1800,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"behavioral heuristics failed\n{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
