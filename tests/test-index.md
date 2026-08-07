# Test Index

Last updated: 2026-08-06

| Test or evidence set | Status | Reproducibility | Current interpretation |
|---|---|---|---|
| `test_skill_validators.py` | current — 143 tests passing | executable, committed fixtures | Structural and declared-semantic regression evidence only. Includes partner-experience instruction checks: Co-design cadence rules present, worked-example checkpoints present, staged rubric clarification, state-files-as-records, and Auto/interactive paragraph symmetry — these lock the instructions, not the behavior; the behavioral matrix remains the arbiter |
| `check_repository.py` | current — passing | executable | Local links, runtime inventory, and resource routing |
| `audit_privacy.py` | current — passing | executable plus human audit | Pattern screen; not proof of privacy safety |
| `faculty-review-scenarios.md` + `evaluator-rubric.md` | current prompt/rubric set — **rerun due** | reproducible when client/model/result metadata are recorded | Behavioral matrix. The 2026-08-06 instruction-level revisions (two new references, syllabus pattern, palette provenance behavior, Co-design cadence and partner-experience rules, Focused-tier overhead rule) trigger this row's rerun rule, and the five scenarios added 2026-08-06 — Co-design cadence, Focused-tier overhead, Supplied accreditation outcomes, Syllabus authorities, Rubric co-design — have never been run. The Co-design cadence and Rubric co-design scenarios respond to owner-reported live behavior: questions were asked only at intake despite the Co-design default. |
| `remediation-forward-test-report.md` + `remediation-forward-test-results.json` | historical/provisional — insufficient metadata and retained evidence | prompt/rubric hashes retained; exact model, evaluator, responses, and excerpts missing | Exploratory observations only; rerun the current matrix before citing passing behavioral evidence |
| `forward-test-report.md` | historical/superseded | narrative only | Documents early failures and fixes; not current package inventory |
| `rich-artifact-production-report.md` | historical bounded pass | not independently reproducible because temporary files were not retained | Evidence about one past host/toolchain only |
| `rich-artifact-fixture-spec.md` | current rerun contract | specification committed; rerun pending | Defines what a reproducible future rich-artifact result must retain |
| `run_behavioral_scenarios.py` + `behavioral-results/` | current — live opt-in runner | reproducible given an OpenAI-compatible endpoint (defaults to the sibling `course_development_partner_app/.env`, `gpt-oss:120b` via Purdue GenAI); full transcripts, prompt/skill hashes, model id, and dates retained per record | Automated heuristic screen of the partner-experience scenarios (Co-design cadence, Rubric co-design, Focused-tier overhead), with scripted educator replies and majority scoring over `--iterations`. First live records (2026-08-06): cadence and focused passed; rubric passed 2 of 3 iterations. Heuristic passes are a screen — a qualifying forward-test pass still requires a human applying `evaluator-rubric.md` to the retained transcripts. `test_behavioral_live.py` folds the runner into the unit suite only when `RUN_LIVE_BEHAVIORAL=1`. |
| Live external-action authorization | pending | no faithful mock committed | Unsupported as a tested claim |
| Identifiable-data refusal | pending behavioral rerun | prompt/rubric needed before release claim | Core instructions prohibit use, but client behavior is unverified |
| Independent scorer consistency | pending behavioral rerun | requires qualified-human fixture/judgments | Do not claim grading consistency |
| Bidirectional cross-client handoff | pending | requires named-client runs | Compatibility remains conditional |

When a result is rerun, preserve a machine-readable record outside the runtime skill with the scenario ID, prompt hash/version, client/model, date, evaluator, applicable rubric IDs, observations, result, and limitations.

## Renamed terms

The default interaction mode formerly named **Studio** is now **Co-design**, renamed to avoid collision with studio-format course delivery in STEM. `forward-test-report.md` documents runs actually performed under the old name and is left unedited; one residual "Studio" mention remains in `evaluator-rubric.md`. Read "Studio" as "Co-design" when applying historical records to a current run.

`faculty-review-scenarios.md` and `evaluator-rubric.md` are working documents, not frozen records: both have been revised since the initial hashes were pinned (palette-provenance wording on 2026-08-06, and four new scenarios the same day). `remediation-forward-test-results.json` preserves both the **initial** hashes — tying its recorded observations to the exact text they were produced against — and the **current** hashes, which the unit suite re-pins on every conscious edit so that silent drift fails a test. Recorded results speak only for the initial text; the current text defines the next rerun.
