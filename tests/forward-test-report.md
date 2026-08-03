# Initial Forward-Test Report

> Historical and superseded as a current inventory/status record. Retained to document the initial failures and revisions. See `test-index.md` for current status and `rich-artifact-production-report.md` for the later bounded production exercise.
>
> The default interaction mode named "Studio" below was later renamed **Co-design**, to avoid collision with studio-format course delivery in STEM. This record is left unedited because it documents runs actually performed against the earlier name.

Date: 2026-07-31

Skill: `course-development-partner`

## Package inventory

```text
course-development-partner/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── alignment-map.md
│   ├── artifact-manifest.md
│   ├── capability-manifest.md
│   ├── context-brief.md
│   ├── course-design-brief.md
│   ├── design-log.md
│   └── lesson-storyboard.md
├── references/
│   ├── artifact-patterns.md
│   ├── design-workflow.md
│   ├── interaction-protocol.md
│   ├── mcp-capability-contracts.md
│   ├── portability.md
│   ├── tool-routing.md
│   └── validation-checklists.md
└── scripts/
    ├── validate_alignment_map.py
    ├── validate_artifact_manifest.py
    └── validate_design_state.py
```

Development-only planning and tests remain outside the runtime skill package.

## Method

Fresh agents received only the skill path and a realistic professor request. They were instructed to return the response they would give and not edit files. Expected answers and suspected failure modes were not included.

## STEM active-learning redesign

Request: redesign a 50-minute sophomore cell-biology lecture on membrane transport into active learning, with a worksheet and instructor guide.

Result: passed the initial test.

Observed strengths:

- offered Studio, Guided, and Rapid modes;
- proposed an alignment preview and progressive task sequence;
- surfaced working assumptions;
- asked one pivotal question about qualitative versus quantitative treatment before producing full artifacts;
- included accessibility and contingency considerations.

## Non-STEM discussion design

Request: design a rigorous 75-minute upper-level history activity comparing how two primary sources construct political legitimacy.

Initial result: important interaction failure.

The response produced a strong activity but silently selected Rapid mode rather than defaulting to Studio and allowing the instructor to choose.

Revision:

- strengthened `SKILL.md` and `references/interaction-protocol.md` to require Studio by default;
- prohibited silently choosing Guided or Rapid because a request appears complete.

Retest result: passed.

The response explicitly activated Studio mode, exposed assumptions, presented an alignment preview, and asked for the two source texts before full worksheet production.

## Rubric calibration

Request: refine a 10-point reaction-engineering rubric using three de-identified response summaries.

Initial result: important calibration failure.

The response proposed a sensible balanced rubric but assigned provisional scores before asking the instructor to choose a scoring orientation or supply their judgments about what the examples demonstrated.

Revision:

- required explicit choice among objective-achievement, error/deduction, and balanced orientations;
- prohibited inferring orientation from the existing rubric;
- required response content or confirmation that summaries are sufficient;
- required instructor judgments before scoring calibration examples.

Retest result: passed.

The response labeled the rubric architecture provisional, recommended balanced/objective-first scoring, explained all three orientations, and asked the instructor to approve the orientation, clarify the role of calculations, and judge attainment in each example before scoring.

## Remaining forward tests

- tool-limited client fallback;
- mock LMS read/draft/publish authorization;
- full artifact-family production and rendered verification;
- cross-client ChatGPT-to-Claude and Claude-to-ChatGPT handoff;
- identifiable-student-data privacy refusal;
- independent grading consistency using full de-identified responses.
