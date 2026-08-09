# Artifact Manifest

- Schema version: 1.0
- Last updated:

| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review | Data-task-fit evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | markdown |  |  |  |  |  |  | draft |  |  |  |  |  | not required | not applicable — no dataset |

Status values: `draft`, `review`, `validated`, `teaching-ready`, `retired`.

Use `Artifact family` to group connected versions. When a paired family is required, write `student; instructor` in `Required variants` on at least one family row and label each row's `Variant` explicitly. Leave all three family columns blank for a standalone artifact.

Artifact types: `markdown`, `document`, `presentation`, `spreadsheet`, `pdf`, `visual`, `audio`, `video`, `other`.

Validation tokens: `technical`, `alignment`, `source/reuse`, `structural`, `rendered/playback`, `accessibility`, `privacy/metadata`, `reopen`, `manual`, `data-task-fit`.

Every teaching-ready artifact must declare `Data-task-fit evidence`. When the artifact gives students a dataset or asks them to produce a chart or statistic, link the row in `data-task-record.md` recording the executed check, and carry the `data-task-fit` validation token; when no dataset is involved, write `not applicable — no dataset`. The token may never stand alone: a token without a linked record is an unverifiable claim, and `scripts/validate_data_task_record.py` re-runs the linked record against the dataset it names. Record the check only after executing the requested operation on the exact supplied file per `references/data-task-fit.md`.

Use ISO dates. A rich artifact marked `teaching-ready` must link its production plan and every teaching-ready artifact must link its accessibility review or a bounded review record explaining why specialized review was not applicable.

Every teaching-ready artifact must also declare `Safety review` rather than leaving it blank: link the approved `safety-review.md` from `assets/safety-review.md` when students will encounter a physical hazard, or write `not required` when the artifact involves none. A plain local review reference must end in `.md`, `.pdf`, `.doc`, `.docx`, `.odt`, `.rtf`, `.txt`, `.html`, or `.htm`; filenames may contain spaces. `pending`, `draft`, `review`, `blocked`, `unverified`, a bare `approved` status, and prose approval statements are not review references and cannot support teaching-ready status. The declaration is required because this skill cannot detect hazards; the responsible safety owner, not the validator, makes the determination.
