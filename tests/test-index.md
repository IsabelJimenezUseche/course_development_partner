# Test Index

Last updated: 2026-08-01

| Test or evidence set | Status | Reproducibility | Current interpretation |
|---|---|---|---|
| `test_skill_validators.py` | current — 114 tests passing | executable, committed fixtures | Structural and declared-semantic regression evidence only |
| `check_repository.py` | current — passing | executable | Local links, runtime inventory, and resource routing |
| `audit_privacy.py` | current — passing | executable plus human audit | Pattern screen; not proof of privacy safety |
| `faculty-review-scenarios.md` + `evaluator-rubric.md` | current prompt/rubric set | reproducible when client/model/result metadata are recorded | Behavioral matrix; rerun after instruction-level changes |
| `remediation-forward-test-report.md` + `remediation-forward-test-results.json` | historical/provisional — insufficient metadata and retained evidence | prompt/rubric hashes retained; exact model, evaluator, responses, and excerpts missing | Exploratory observations only; rerun the current matrix before citing passing behavioral evidence |
| `forward-test-report.md` | historical/superseded | narrative only | Documents early failures and fixes; not current package inventory |
| `rich-artifact-production-report.md` | historical bounded pass | not independently reproducible because temporary files were not retained | Evidence about one past host/toolchain only |
| `rich-artifact-fixture-spec.md` | current rerun contract | specification committed; rerun pending | Defines what a reproducible future rich-artifact result must retain |
| Live external-action authorization | pending | no faithful mock committed | Unsupported as a tested claim |
| Identifiable-data refusal | pending behavioral rerun | prompt/rubric needed before release claim | Core instructions prohibit use, but client behavior is unverified |
| Independent scorer consistency | pending behavioral rerun | requires qualified-human fixture/judgments | Do not claim grading consistency |
| Bidirectional cross-client handoff | pending | requires named-client runs | Compatibility remains conditional |

When a result is rerun, preserve a machine-readable record outside the runtime skill with the scenario ID, prompt hash/version, client/model, date, evaluator, applicable rubric IDs, observations, result, and limitations.

## Renamed terms

The default interaction mode formerly named **Studio** is now **Co-design**, renamed to avoid collision with studio-format course delivery in STEM. `evaluator-rubric.md`, `faculty-review-scenarios.md`, and `forward-test-report.md` still use the earlier name and are intentionally left unedited: the first two are hash-pinned in `remediation-forward-test-results.json` so that recorded results stay tied to the exact text they were produced against, and the third documents runs actually performed under the old name. Read "Studio" as "Co-design" when applying them to a current run.
