#!/usr/bin/env python3
"""Run partner-experience behavioral scenarios against a live model.

Drives selected forward-test scenarios from ``faculty-review-scenarios.md``
against an OpenAI-compatible chat-completions endpoint — by default the Purdue
GenAI configuration found in the sibling ``course_development_partner_app/.env``
— and applies deterministic heuristics to the transcript. The skill text itself
is the system prompt, so this exercises the portable skill in a minimal client,
not the app.

Heuristic results are a screen, not qualifying evidence. A qualifying pass
still requires a human evaluator applying ``evaluator-rubric.md`` to the
retained transcript; this runner preserves every transcript in full for that
purpose under ``tests/behavioral-results/``.

Environment variables (a ``.env`` file fills in only the ones not already set):
  PURDUE_GENAI_BASE_URL, PURDUE_GENAI_CHAT_PATH, PURDUE_GENAI_MODEL_ID,
  PURDUE_GENAI_API_KEY, PURDUE_GENAI_TIMEOUT_SECONDS, PURDUE_GENAI_MAX_TOKENS

Exit codes:
  0: every selected scenario passed its heuristics
  1: configuration or transport error
  2: one or more heuristic failures
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "course-development-partner"
SCENARIO_FILE = ROOT / "tests" / "faculty-review-scenarios.md"
RESULTS_DIR = ROOT / "tests" / "behavioral-results"
DEFAULT_ENV = ROOT.parent / "course_development_partner_app" / ".env"

INVITE_PHRASES = (
    "?",
    "decide for me",
    "your choice",
    "your call",
    "let me know",
    "once you",
    "after you",
    "when you",
    "which of",
    "does this match",
    "sound right",
    "shall i",
    "should i",
)

TIER_MODE_TOKENS = (
    "Co-design",
    "engagement tier",
    "Engagement tier",
    "Focused tier",
    "Focused-tier",
    "Guided mode",
    "Rapid mode",
    "Auto mode",
    "state file",
    "state-file",
    "course-design-brief",
    "project-index",
    "design log",
    "design-log",
)


Check = Callable[[str], tuple[bool, str]]


def count_questions(text: str) -> int:
    return text.count("?")


# Counting question marks cannot see the owner's primary failure mode. A reply
# that bundles "Decision 1 / Decision 2 / Decision 3", each with its own option
# list and choice prompt, contains only three question marks and passes a
# 1..4 question check while violating "one decision per turn" three times over.
# These patterns count the decision cards themselves.
# `[^\S\r\n]` is any horizontal whitespace including the U+202F narrow no-break
# space and U+00A0 that models emit inside headings; a literal `[ \t]` misses them.
DECISION_MARKER = re.compile(
    r"^[^\S\r\n]{0,3}(?:#{1,6}[^\S\r\n]*)?\**[^\S\r\n]*Decision"
    r"[^\S\r\n]*(?:\d+|[A-Z])?[^\S\r\n]*[:\-‐-―]",
    re.IGNORECASE | re.MULTILINE,
)
OPTION_BLOCK = re.compile(
    r"^[^\S\r\n]{0,3}\**[^\S\r\n]*Options\b", re.IGNORECASE | re.MULTILINE
)
CHOICE_PROMPT = re.compile(
    r"your choice|pick one|choose one|select one|choose, modify",
    re.IGNORECASE,
)


def count_decision_cards(text: str) -> tuple[int, int, int]:
    """Return (decision markers, option blocks, choice-prompt lines) in one reply.

    Choice prompts are counted per line, not per match: the card template's own
    closing line ("Your choice: choose, modify, or say 'decide for me.'") hits
    several alternations at once and must count as the single prompt it is.
    """
    prompt_lines = sum(
        1 for line in text.splitlines() if CHOICE_PROMPT.search(line)
    )
    return (
        len(DECISION_MARKER.findall(text)),
        len(OPTION_BLOCK.findall(text)),
        prompt_lines,
    )


def check_single_decision_per_turn(text: str) -> tuple[bool, str]:
    markers, options, prompts = count_decision_cards(text)
    worst = max(markers, options, prompts)
    return worst <= 1, (
        f"decision markers {markers}, option blocks {options}, "
        f"choice prompts {prompts} (at most 1 each)"
    )


# Topic words alone are not a rejection: a reply that says "the data are
# categorical" and then produces the scatter plot passed the earlier version of
# this check. A pass has to refuse the requested representation, so the phrase
# must join an inability to the request.
DATA_REJECTION_PATTERNS = (
    r"(?:can(?:no|')t|cannot|won'?t|does ?n[o']t|isn'?t able to|unable to)\s+"
    r"(?:\w+\s+){0,6}?(?:support|produce|make|create|plot|generate|be plotted|be used)",
    r"(?:not|no)\s+(?:\w+\s+){0,3}?(?:possible|appropriate|suitable|valid)\s+"
    r"(?:\w+\s+){0,4}?(?:scatter|with (?:this|these|the supplied))",
    r"(?:scatter\s*(?:plot|chart)?)\s+(?:\w+\s+){0,4}?"
    r"(?:is|are)\s+(?:not|inappropriate|impossible|unsuitable)",
    r"(?:no|not|lacks?|missing|without)\s+(?:\w+\s+){0,4}?paired\b",
    r"(?:only|just|single)\s+(?:one|1)\s+(?:row|observation|value)\s+per\b",
    r"(?:instead of|rather than|in place of)\s+(?:a\s+)?scatter",
)
# What the reply must offer or ask for once it has refused: the honest routes in
# references/data-task-fit.md §5.
DATA_REPAIR_TOKENS = (
    "bar chart",
    "bar graph",
    "change the task",
    "change the dataset",
    "different representation",
    "raw data",
    "per-student",
    "individual observations",
    "second quantitative",
    "two quantitative",
    "underlying data",
)
# Markers that the reply went ahead and produced the impossible chart.
SCATTER_PRODUCTION_PATTERNS = (
    r"(?:here(?:'s| is)|below is|i(?:'ve| have) (?:created|made|produced|plotted))"
    r"[^.\n]{0,40}scatter",
    r"\.scatter\s*\(",
    r"plt\.scatter",
    r"geom_point\s*\(",
    r"(?:kind|type)\s*=\s*[\"']scatter",
    r"chart\s*type\s*:\s*scatter",
)


def _matches_any(patterns: tuple[str, ...], text: str) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]


def check_flags_data_mismatch(text: str) -> tuple[bool, str]:
    """The activity asks for a scatter plot from one row per category.

    A pass refuses the requested representation and names a route out of the
    mismatch. Mentioning "categorical" is topic, not refusal — the earlier
    version of this check passed a reply that named the word and then produced
    the chart anyway.
    """
    rejections = _matches_any(DATA_REJECTION_PATTERNS, text)
    lowered = text.lower()
    repairs = [token for token in DATA_REPAIR_TOKENS if token in lowered]
    if not rejections:
        return False, "no explicit refusal of the requested scatter plot"
    if not repairs:
        return False, (
            f"refused the scatter plot ({len(rejections)} phrase(s)) but offered no "
            "repair: a different representation, the missing variable, or a changed task"
        )
    return True, f"refuses the representation and offers a repair ({repairs[:3]})"


def check_does_not_produce_scatter(text: str) -> tuple[bool, str]:
    """Naming the mismatch and then producing the chart is still the failure."""
    produced = _matches_any(SCATTER_PRODUCTION_PATTERNS, text)
    if produced:
        return False, f"produced the impossible scatter plot anyway ({produced[:2]})"
    return True, "did not produce the requested scatter plot"


def check_no_invented_observations(text: str) -> tuple[bool, str]:
    """Fabricating per-student rows to rescue the chart is the silent-substitution
    failure the gate exists to prevent; inventing data must be disclosed."""
    lowered = text.lower()
    invented = any(
        token in lowered
        for token in ("simulated", "synthetic", "made-up", "sample data i generated")
    )
    disclosed = any(
        token in lowered
        for token in ("disclose", "constructed for teaching", "generated for teaching",
                      "not observed", "illustrative")
    )
    if invented and not disclosed:
        return False, "introduced substitute data without disclosing it as constructed"
    return True, "no undisclosed substitute data"


def check_questions_between(low: int, high: int) -> Check:
    def check(text: str) -> tuple[bool, str]:
        count = count_questions(text)
        ok = low <= count <= high
        return ok, f"question marks {count} (expected {low}..{high})"

    check.__name__ = f"questions_between_{low}_{high}"
    return check


def check_word_count_under(limit: int) -> Check:
    def check(text: str) -> tuple[bool, str]:
        count = len(text.split())
        return count <= limit, f"word count {count} (limit {limit})"

    check.__name__ = f"word_count_under_{limit}"
    return check


def check_word_count_at_least(minimum: int) -> Check:
    def check(text: str) -> tuple[bool, str]:
        count = len(text.split())
        return count >= minimum, f"word count {count} (minimum {minimum})"

    check.__name__ = f"word_count_at_least_{minimum}"
    return check


REQUEST_PHRASES = (
    "let me know",
    "decide for me",
    "your choice",
    "your call",
    "would you like",
    "do you want",
    "should i",
    "shall i",
    "which of these",
    "which option",
    "please confirm",
    "awaiting your",
    "feedback",
)


def check_no_closing_request(text: str) -> tuple[bool, str]:
    # Question marks are allowed anywhere: student-facing content legitimately
    # contains questions. Only an explicit request to the educator fails.
    tail = text[int(len(text) * 0.75) :].lower()
    hits = [phrase for phrase in REQUEST_PHRASES if phrase in tail]
    if hits:
        return False, f"Auto output ends by requesting educator input: {hits}"
    return True, "no closing request for feedback or a choice"


def check_tail_mentions_any(*tokens: str) -> Check:
    def check(text: str) -> tuple[bool, str]:
        tail = text[int(len(text) * 0.6) :].lower()
        hits = [token for token in tokens if token.lower() in tail]
        if hits:
            return True, f"closing section mentions {hits}"
        return False, f"closing section mentions none of {list(tokens)}"

    check.__name__ = "tail_mentions_any_" + "_".join(t.split()[0] for t in tokens)
    return check


def check_returns_to_educator(text: str) -> tuple[bool, str]:
    tail = text[int(len(text) * 0.6) :].lower()
    for phrase in INVITE_PHRASES:
        if phrase in tail:
            return True, f"turn ends with a return to the educator ({phrase!r})"
    return False, "no question or invitation in the closing part of the turn"


def check_no_tier_mode_talk(text: str) -> tuple[bool, str]:
    hits = [token for token in TIER_MODE_TOKENS if token in text]
    if hits:
        return False, f"tier/mode/state machinery surfaced: {hits}"
    return True, "tiers, modes, and state files stayed invisible"


def check_mentions_any(*tokens: str) -> Check:
    def check(text: str) -> tuple[bool, str]:
        lowered = text.lower()
        hits = [token for token in tokens if token.lower() in lowered]
        if hits:
            return True, f"mentions {hits}"
        return False, f"mentions none of {list(tokens)}"

    check.__name__ = "mentions_any_" + "_".join(t.split()[0] for t in tokens)
    return check


@dataclass
class Turn:
    """One educator message and the checks applied to the model's reply."""

    educator_message: str | None  # None means: use the scenario prompt
    checks: list[Check]


@dataclass
class Scenario:
    scenario_id: str
    heading: str  # heading in faculty-review-scenarios.md; prompt is extracted
    references: list[str]
    turns: list[Turn]
    rubric_row: str = ""
    notes: str = ""


SCENARIOS: dict[str, Scenario] = {
    scenario.scenario_id: scenario
    for scenario in [
        Scenario(
            scenario_id="codesign-cadence",
            heading="Co-design cadence",
            references=["interaction-protocol.md"],
            rubric_row="Co-design cadence",
            notes=(
                "Owner-reported failure mode: questions only at intake, then a "
                "one-pass module. Heuristics check that each turn stays small "
                "and returns to the educator."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_questions_between(1, 4),
                        check_single_decision_per_turn,
                        check_word_count_under(700),
                        check_returns_to_educator,
                    ],
                ),
                Turn(
                    educator_message=(
                        "Second-year mechanical engineering students, about 40 "
                        "of them. They can execute single conversions but fall "
                        "apart with mixed unit systems under time pressure. The "
                        "module runs in two 75-minute sessions per week. Your "
                        "recommendation is fine on everything else."
                    ),
                    checks=[
                        check_word_count_under(900),
                        check_single_decision_per_turn,
                        check_returns_to_educator,
                    ],
                ),
                Turn(
                    educator_message=(
                        "Yes, that sequence works for me. Start with the lesson "
                        "outline."
                    ),
                    checks=[
                        check_word_count_under(1100),
                        check_returns_to_educator,
                    ],
                ),
            ],
        ),
        Scenario(
            scenario_id="rubric-codesign",
            heading="Rubric co-design",
            references=["interaction-protocol.md", "artifact-patterns.md"],
            rubric_row="Rubric co-design",
            notes=(
                "The interrogation anti-pattern fires the full clarification "
                "list at once; staged clarification asks at most three "
                "architecture questions, then proposes reviewable defaults."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_questions_between(1, 4),
                        check_word_count_under(800),
                        check_mentions_any("orientation", "objective"),
                        check_returns_to_educator,
                    ],
                ),
                Turn(
                    educator_message=(
                        "The objective is that students justify whether two "
                        "measured values differ using their uncertainties. "
                        "Summative, scored as part of the lab report. Your "
                        "balanced idea sounds right - go with that."
                    ),
                    # A legitimate staged proposal (criteria + weights +
                    # descriptors, final rubric deferred) measured 1152 words
                    # on the first live run; a finished-rubric-plus-grader-guide
                    # dump runs well past 1400.
                    checks=[
                        check_word_count_under(1400),
                        check_mentions_any("weight", "criteri"),
                        check_returns_to_educator,
                    ],
                ),
            ],
        ),
        Scenario(
            scenario_id="auto-noninteractive",
            heading="Auto non-interactive design",
            references=["interaction-protocol.md"],
            rubric_row="Auto non-interactive design",
            notes=(
                "The mode contrast: Auto must NOT interact. A completed draft, "
                "reported assumptions and limitations, and no closing request "
                "for a choice or feedback. Question marks are permitted "
                "anywhere (student-facing content contains questions)."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_word_count_at_least(400),
                        check_no_closing_request,
                        check_mentions_any("assumption", "assumed"),
                        check_mentions_any(
                            "limitation", "provisional", "owner review", "blocked"
                        ),
                    ],
                ),
            ],
        ),
        Scenario(
            scenario_id="rapid-single-review",
            heading="Rapid single-review design",
            references=["interaction-protocol.md"],
            rubric_row="Rapid single-review design",
            notes=(
                "Rapid produces the complete provisional draft in one pass and "
                "ends with exactly one consolidated review section - neither "
                "intermediate checkpoints (Co-design) nor no review at all "
                "(Auto)."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_word_count_at_least(400),
                        check_mentions_any("provisional", "assumption", "assumed"),
                        check_tail_mentions_any("review", "decision", "confirm"),
                    ],
                ),
            ],
        ),
        Scenario(
            scenario_id="data-task-fit",
            heading="Data-task fit",
            references=["data-task-fit.md"],
            rubric_row="Data-task fit",
            notes=(
                "Owner-reported failure: a scatter plot requested from "
                "categorical aggregate data. Passing requires rejecting or "
                "repairing the mismatch rather than producing the chart or "
                "quietly substituting different data."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_flags_data_mismatch,
                        check_does_not_produce_scatter,
                        check_no_invented_observations,
                    ],
                ),
            ],
        ),
        Scenario(
            scenario_id="focused-overhead",
            heading="Focused-tier overhead",
            references=["interaction-protocol.md"],
            rubric_row="Focused-tier overhead",
            notes=(
                "A small request should get the artifact (or one brief "
                "clarification) with the tier/mode/state machinery invisible. "
                "Producing the worksheet in a single turn is correct here, so "
                "no word cap applies."
            ),
            turns=[
                Turn(
                    educator_message=None,
                    checks=[
                        check_no_tier_mode_talk,
                        check_questions_between(0, 3),
                    ],
                ),
            ],
        ),
    ]
}


@dataclass
class Config:
    base_url: str
    chat_path: str
    model_id: str
    api_key: str
    timeout: float
    max_tokens: int

    @property
    def chat_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.chat_path.lstrip('/')}"


def load_env_file(path: Path) -> None:
    """Fill os.environ from a KEY=VALUE file without overriding set values."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def build_config(args: argparse.Namespace) -> Config:
    load_env_file(Path(args.env).expanduser())
    api_key = os.environ.get("PURDUE_GENAI_API_KEY", "").strip()
    model_id = (args.model or os.environ.get("PURDUE_GENAI_MODEL_ID", "")).strip()
    if not api_key or not model_id:
        raise RuntimeError(
            "PURDUE_GENAI_API_KEY and PURDUE_GENAI_MODEL_ID must be set (via "
            f"environment or {args.env})"
        )
    return Config(
        base_url=os.environ.get(
            "PURDUE_GENAI_BASE_URL", "https://genai.rcac.purdue.edu"
        ),
        chat_path=os.environ.get("PURDUE_GENAI_CHAT_PATH", "/api/chat/completions"),
        model_id=model_id,
        api_key=api_key,
        timeout=float(os.environ.get("PURDUE_GENAI_TIMEOUT_SECONDS", "120")),
        max_tokens=args.max_tokens
        or int(os.environ.get("PURDUE_GENAI_MAX_TOKENS", "3000")),
    )


def extract_scenario_prompt(heading: str) -> str:
    text = SCENARIO_FILE.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Scenario heading not found: {heading!r}")
    return match.group(1).strip()


def build_system_prompt(references: list[str]) -> str:
    parts = [
        "You are a teaching-focused assistant in a live chat with an educator. "
        "The following Agent Skill is installed and governs your behavior. "
        "Reply with your next conversational turn only.",
        "\n\n=== SKILL.md ===\n",
        (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
    ]
    for name in references:
        parts.append(f"\n\n=== references/{name} ===\n")
        parts.append((SKILL_ROOT / "references" / name).read_text(encoding="utf-8"))
    parts.append(
        "\n\n(Other references and assets from the skill package exist but are "
        "not included in this session.)"
    )
    return "".join(parts)


def call_model(config: Config, messages: list[dict]) -> str:
    payload = json.dumps(
        {
            "model": config.model_id,
            "messages": messages,
            "stream": False,
            "max_tokens": config.max_tokens,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        config.chat_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=config.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("Model returned an empty response")
            return content
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(10)
    raise RuntimeError(f"Model call failed after retry: {last_error}")


def run_scenario_once(config: Config, scenario: Scenario, iteration: int) -> dict:
    prompt = extract_scenario_prompt(scenario.heading)
    messages: list[dict] = [
        {"role": "system", "content": build_system_prompt(scenario.references)}
    ]
    turn_records: list[dict] = []
    scenario_pass = True
    for index, turn in enumerate(scenario.turns, start=1):
        educator_message = turn.educator_message or prompt
        messages.append({"role": "user", "content": educator_message})
        response = call_model(config, messages)
        messages.append({"role": "assistant", "content": response})
        check_records = []
        for check in turn.checks:
            ok, detail = check(response)
            check_records.append(
                {"check": check.__name__, "ok": ok, "detail": detail}
            )
            status = "PASS" if ok else "FAIL"
            print(
                f"{status}: {scenario.scenario_id} run {iteration} "
                f"turn {index}: {detail}"
            )
            scenario_pass = scenario_pass and ok
        turn_records.append(
            {
                "turn": index,
                "educator_message": educator_message,
                "model_response": response,
                "checks": check_records,
            }
        )
    return {
        "iteration": iteration,
        "heuristic_result": "heuristic-pass" if scenario_pass else "heuristic-fail",
        "turns": turn_records,
    }


def run_scenario(config: Config, scenario: Scenario, iterations: int) -> dict:
    runs = [
        run_scenario_once(config, scenario, iteration)
        for iteration in range(1, iterations + 1)
    ]
    passes = sum(1 for run in runs if run["heuristic_result"] == "heuristic-pass")
    # Model outputs vary run to run; with several iterations a strict majority
    # must pass (a tie fails).
    overall = "heuristic-pass" if passes * 2 > len(runs) else "heuristic-fail"
    print(
        f"{scenario.scenario_id}: passed {passes} of {len(runs)} iteration(s) "
        f"-> {overall}"
    )
    return {
        "scenario_id": scenario.scenario_id,
        "rubric_row": scenario.rubric_row,
        "notes": scenario.notes,
        "references_in_context": scenario.references,
        "iterations_run": len(runs),
        "iterations_passed": passes,
        "heuristic_result": overall,
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--env",
        default=str(DEFAULT_ENV),
        help="Path to a .env file supplying PURDUE_GENAI_* values "
        "(default: sibling course_development_partner_app/.env)",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="Scenario to run (repeatable; default: all)",
    )
    parser.add_argument("--model", help="Override the model id")
    parser.add_argument("--max-tokens", type=int, default=0)
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Runs per scenario; a strict majority must pass (default 1)",
    )
    parser.add_argument("--list", action="store_true", help="List scenarios and exit")
    args = parser.parse_args()

    if args.list:
        for scenario in SCENARIOS.values():
            print(f"{scenario.scenario_id}: {scenario.heading}")
        return 0

    try:
        config = build_config(args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    selected = args.scenario or sorted(SCENARIOS)
    results = []
    try:
        for scenario_id in selected:
            results.append(
                run_scenario(config, SCENARIOS[scenario_id], max(1, args.iterations))
            )
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    record = {
        "schema_version": "1.0",
        "date": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "client": "direct chat-completions (skill text as system prompt)",
        "endpoint": config.base_url,
        "model": config.model_id,
        "max_tokens": config.max_tokens,
        "evaluator": "automated heuristics (run_behavioral_scenarios.py)",
        "scenario_file_sha256": hashlib.sha256(
            SCENARIO_FILE.read_bytes()
        ).hexdigest(),
        "skill_file_sha256": hashlib.sha256(
            (SKILL_ROOT / "SKILL.md").read_bytes()
        ).hexdigest(),
        "results": results,
        "limitations": [
            "Automated heuristics only; not qualifying evidence. A qualifying "
            "pass requires a human evaluator applying evaluator-rubric.md to "
            "the retained transcripts in this record.",
            "Scripted educator replies; a live educator may behave differently.",
            "Single run; model outputs vary across runs.",
        ],
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", config.model_id)
    output_path = RESULTS_DIR / f"{stamp}-{model_slug}.json"
    output_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Record: {output_path.relative_to(ROOT)}")

    failures = [r for r in results if r["heuristic_result"] != "heuristic-pass"]
    if failures:
        print(f"FAIL: {len(failures)} of {len(results)} scenarios failed heuristics")
        return 2
    print(f"OK: {len(results)} scenarios passed heuristics (human review still required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
