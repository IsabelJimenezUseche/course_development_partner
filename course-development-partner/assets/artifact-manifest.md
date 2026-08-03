# Artifact Manifest

- Schema version: 1.0
- Last updated:

| Artifact ID | Artifact type | Artifact family | Variant | Required variants | File or reference | Audience | Outcome(s) | Status | Validation completed | Blockers/open issues | Last reviewed | Production plan | Accessibility review | Safety review |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | markdown |  |  |  |  |  |  | draft |  |  |  |  |  | not required |

Status values: `draft`, `review`, `validated`, `teaching-ready`, `retired`.

Use `Artifact family` to group connected versions. When a paired family is required, write `student; instructor` in `Required variants` on at least one family row and label each row's `Variant` explicitly. Leave all three family columns blank for a standalone artifact.

Artifact types: `markdown`, `document`, `presentation`, `spreadsheet`, `pdf`, `visual`, `audio`, `video`, `other`.

Validation tokens: `technical`, `alignment`, `source/reuse`, `structural`, `rendered/playback`, `accessibility`, `privacy/metadata`, `reopen`, `manual`.

Use ISO dates. A rich artifact marked `teaching-ready` must link its production plan and every teaching-ready artifact must link its accessibility review or a bounded review record explaining why specialized review was not applicable.

Every teaching-ready artifact must also declare `Safety review` rather than leaving it blank: link the approved `safety-review.md` from `assets/safety-review.md` when students will encounter a physical hazard, or write `not required` when the artifact involves none. `pending`, `draft`, `review`, `blocked`, `unverified`, and a bare `approved` status are not review references and cannot support teaching-ready status. The declaration is required because this skill cannot detect hazards; the responsible safety owner, not the validator, makes the determination.
