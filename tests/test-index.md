# Test Index

Last updated: 2026-08-01

| Test or evidence set | Status | Reproducibility | Current interpretation |
|---|---|---|---|
| `test_skill_validators.py` | current — 51 tests passing | executable, committed fixtures | Structural and declared-semantic regression evidence only |
| `check_repository.py` | current — passing | executable | Local links, runtime inventory, and resource routing |
| `audit_privacy.py` | current — passing | executable plus human audit | Pattern screen; not proof of privacy safety |
| `faculty-review-scenarios.md` + `evaluator-rubric.md` | current prompt/rubric set | reproducible when client/model/result metadata are recorded | Behavioral matrix; rerun after instruction-level changes |
| `remediation-forward-test-report.md` + `remediation-forward-test-results.json` | current — five focused probes passed after one visual-boundary revision/retest | fresh-agent narrative and machine-readable result with prompt/rubric hashes | Bounded instruction-level evidence in one agent environment |
| `forward-test-report.md` | historical/superseded | narrative only | Documents early failures and fixes; not current package inventory |
| `rich-artifact-production-report.md` | historical bounded pass | not independently reproducible because temporary files were not retained | Evidence about one past host/toolchain only |
| `rich-artifact-fixture-spec.md` | current rerun contract | specification committed; rerun pending | Defines what a reproducible future rich-artifact result must retain |
| Live external-action authorization | pending | no faithful mock committed | Unsupported as a tested claim |
| Identifiable-data refusal | pending behavioral rerun | prompt/rubric needed before release claim | Core instructions prohibit use, but client behavior is unverified |
| Independent scorer consistency | pending behavioral rerun | requires qualified-human fixture/judgments | Do not claim grading consistency |
| Bidirectional cross-client handoff | pending | requires named-client runs | Compatibility remains conditional |

When a result is rerun, preserve a machine-readable record outside the runtime skill with the scenario ID, prompt hash/version, client/model, date, evaluator, applicable rubric IDs, observations, result, and limitations.
