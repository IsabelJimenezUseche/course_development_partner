# Validation Checklists

## Contents

1. Severity and reporting
2. Disciplinary and technical validity
3. Constructive alignment
4. Scaffolding and readiness
5. Active-learning feasibility
6. Accessibility, inclusion, and clarity
7. Assessment integrity and fairness
8. Artifact integrity
9. Evidence and source quality
10. STEM authenticity and safety when applicable
11. Implementation feasibility and sustainability
12. Improvement evidence and research boundary
13. Manual equivalents for deterministic checks

## 1. Severity and reporting

Classify each finding:

- **Blocker:** unsafe, invalid, unsolvable, materially unfair, inaccessible for required use, corrupt, or unusable. A hazard-bearing element that is unverified against its authoritative source or unapproved by the responsible safety owner is always a blocker.
- **Important:** likely to weaken learning, alignment, fairness, accessibility, or implementation.
- **Polish:** improves clarity or presentation without changing validity.

Report:

```markdown
Finding: [short title]
Severity: Blocker | Important | Polish
Evidence: [specific location and observation]
Effect: [why it matters]
Recommendation: [focused correction]
Instructor decision required: yes | no
```

Correct unambiguous blockers. Ask the instructor when correction changes educational intent, grading, policy, or acceptable methods.

## 2. Disciplinary and technical validity

- Verify facts, definitions, mechanisms, terminology, and sources.
- Verify equations, units, dimensions, conversions, notation, and significant figures.
- State assumptions, initial/boundary conditions, and simplifications.
- Confirm that the selected model or method fits the scenario.
- Check that provided data yield a valid, meaningful result.
- Independently reproduce quantitative solutions.
- Recognize alternative valid approaches.
- Verify technical accuracy of diagrams, images, graphs, labels, and scales.
- Verify time-sensitive or externally sourced claims with authoritative sources.

## 3. Constructive alignment

- Map each artifact and assessment item to an outcome.
- Record cognitive demand as one controlled token — `remember`, `understand`, `apply`, `analyze`, `evaluate`, `create` — for the target performance, not the hardest sub-step.
- Match cognitive demand across outcome, activity, and assessment. Scaffolding items below the outcome's demand are legitimate; an outcome whose entire active sample sits below its aligned demand is a gap.
- Read the items rather than trusting the tokens. The ranks order kinds of cognition, not difficulty, so a passing automated demand check shows only that the sample is labeled at the outcome's level.
- Ensure every important outcome has learning support and evidence.
- Remove or justify orphan activities and assessments.
- Ensure engagement serves learning rather than replacing it.
- Check that rubric criteria and weights reflect objective importance.
- For course-level work, check prerequisite flow, outcome development, assessment timing, feedback opportunities, and workload across the sequence.

## 4. Scaffolding and readiness

- Activate or support prerequisites.
- Base the expected student model on a diagnostic, inventory, documented research, or instructor observation, and mark it provisional when none was available.
- Distribute practice for an outcome across the sequence rather than massing it in one module; interleave confusable methods once each can be executed; state the in-the-moment performance cost.
- Increase difficulty for a stated reason.
- Keep challenge attainable with available support.
- Surface and address likely misconceptions.
- Elicit the current student model, use evidence to examine it, and re-test a revised model when conceptual change is intended.
- Distinguish conceptual, procedural, computational, and communication needs.
- Remove avoidable load from notation, directions, representations, interfaces, and simultaneous demands.
- Remove supports when independent performance is expected.
- Culminate in interpretation, justification, transfer, or decision-making when appropriate.

## 5. Active-learning feasibility

- Ensure students can understand directions without excessive oral repair.
- Ensure students perform the intended cognitive work.
- Support equitable participation and useful group roles.
- Preserve individual accountability and evidence of individual learning in collaborative work.
- State the team formation basis, avoid isolating a single underrepresented student on a team, and confirm an early team agreement and a process checkpoint before the final deliverable.
- Make purpose, success criteria, and help pathways visible to students, and sequence an attainable early success on the target construct.
- Include checkpoints, feedback, debrief, and closure.
- Fit the stated time, class size, room, staffing, and technology.
- Provide a fallback for time or technology failure.
- Check instructor and TA workload.

## 6. Accessibility, inclusion, and clarity

- Read `references/accessibility-and-compliance.md` and record authority, exact required standard/version/level/scope, source-verification date, policy date, applicable compliance deadline, and local release/remediation date separately.
- Keep ADA, Section 504, institutional policy, WCAG conformance, universal design, and individual accommodations distinct.
- Use concise language and explain necessary jargon.
- Chunk and order instructions.
- Use semantic headings, landmarks, labels, instructions, and meaningful link text.
- Ensure sufficient contrast and legible sizing.
- Avoid color-only meaning.
- Provide alternative text, transcripts, captions, or textual equivalents.
- Check table structure, document language, accessible equations, reading order, and metadata.
- Apply the exact criterion set named by the required target. For WCAG 2.1, keep Parsing 4.1.1 where required. Record WCAG 2.2 additions—including Focus Not Obscured 2.4.11, Dragging Movements 2.5.7, Target Size 2.5.8, Consistent Help 3.2.6, Redundant Entry 3.3.7, and Accessible Authentication 3.3.8—as additional checks unless 2.2 governs.
- Check keyboard-only operation, logical focus order, focus visibility, zoom, reflow, time limits, input errors, and authentication according to the selected version.
- Inspect PDF tags and reading order rather than assuming a visually correct PDF is accessible.
- Verify generated captions, transcripts, descriptions, and alternative text for disciplinary accuracy.
- Include embedded and third-party learning tools in the reviewed scope.
- Avoid irrelevant stereotypes and exclusionary assumptions.
- Match workload, reading level, and background to the audience.
- Respect required accommodations and institutional policy.
- Verify that learner variability, access, participation, and belonging barriers were considered during intake and design rather than only remediated at the end.
- Offer multiple means of engagement, representation, or expression only when they preserve the target construct.
- Combine automated, keyboard, rendered, assistive-technology, and human-content checks in proportion to the artifact and stakes; record untested scope.
- Do not claim WCAG conformance from an automated scan alone or make an ADA/Section 504 compliance or exception determination.
- Record unresolved barriers, responsible owners, interim access, remediation dates, and required institutional approvals in `assets/accessibility-review.md`.

## 7. Assessment integrity and fairness

- Confirm that every item is unambiguous and solvable.
- Check time burden and point balance.
- Remove accidental answer cues and information leakage.
- Ensure the rubric measures intended learning.
- State the intended interpretation or decision and check outcome coverage, under-sampling, and alternative explanations for performance.
- Apply consistent rules across valid approaches.
- Define error propagation and carry-forward credit.
- Detect double penalties.
- Protect identifiable student data.
- Never make consequential grading or academic-integrity decisions solely from AI output.
- Match scorer preparation, moderation, and consistency evidence to the stakes and judgment required.
- Score team product, individual learning, and team process as separate claims; confirm an individual evidence channel for every outcome claimed for an individual.
- Check peer evaluation for observable criteria, advance disclosure of its grade effect, a formative round, confidentiality, instructor review before it affects a grade, a bounded consequence, and bias, reciprocity, retaliation, and small-sample instability.
- Confirm the grading system was supplied rather than inferred, and that the instrument's scoring logic is compatible with it; verify that promised feedback has a real opportunity for use under the revision policy.
- State the permitted-AI context without claiming an assessment is AI-proof.
- Do not call an assessment or rubric validated unless the claimed interpretation and use have proportionate supporting evidence.

## 8. Artifact integrity

- Apply `references/rich-artifact-production.md` and preserve the approved `production-plan.md` when a rich format is promised.
- Open the file in its intended application when possible.
- Render every page, slide, sheet, image, audio segment, or video segment needed for review.
- Check clipping, overflow, overlap, blank pages, broken equations, missing fonts, and corrupt media.
- Verify that promised elements remain editable.
- Label student and instructor versions clearly.
- Verify links, references, citations, and cross-references.
- Confirm file names and manifest entries match.
- Record the last-reviewed date and unresolved issues.
- Verify the editable source, final distribution artifact, renderer/playback evidence, accessibility review, and regeneration method agree with the artifact manifest.

Run the applicable deterministic state, alignment, assessment, curriculum, manifest, and project validators. If tools cannot run, perform their documented checks manually.

## 9. Evidence and source quality

- Identify the source or professor-approved rationale for consequential pedagogical recommendations.
- Represent applicability, strength, uncertainty, and context limits accurately.
- Distinguish institutional requirements, disciplinary sources, learning research, practice guidance, illustrative contexts, and generated content.
- Verify licenses, attribution, adaptation rights, and reuse restrictions.
- Do not let a general recommendation override an authoritative course requirement without an instructor decision.

## 10. STEM authenticity and safety when applicable

- Require disciplinary formulation, analysis, design, experimentation, interpretation, or judgment rather than a themed calculation alone.
- Apply the matching disciplinary profile in `references/stem-authenticity.md` — engineering, computing and data, laboratory and experimental science, or mathematics and quantitative reasoning.
- Verify applicable standards, protocols, multiple constraints, uncertainty, error, risk, and tradeoffs.
- Include safety, welfare, ethical, lifecycle, environmental, social, or stakeholder consequences when they materially affect the decision.
- Allow multiple defensible alternatives when evidence and reasoning support them.
- Require qualified instructor review of consequential technical, safety, ethical, or standards claims.
- Say plainly whether a laboratory activity is confirmatory, structured, guided, or open inquiry; do not describe a known-answer procedure as inquiry.
- For any hazard-bearing element, confirm verification against the authoritative institutional, manufacturer, or safety-data source with its date, and approval by the named responsible safety owner, recorded in `assets/safety-review.md`. Treat an unverified or unreviewed element as a blocker in every mode.
- Confirm every teaching-ready artifact declares `Safety review` in the manifest — a linked review, or `not required` when no physical hazard exists. A blank declaration is an undeclared release decision, not an absent hazard.
- Check accessibility of the physical environment — reach, handling, protective equipment fit, alarms, and software — and record barriers requiring an approved alternative.

## 11. Implementation feasibility and sustainability

- Estimate professor, TA, grader, student, technology-support, and accessibility-support workload.
- Confirm teaching assistants and graders have the decision authority, facilitation guidance, disciplinary preparation, scoring calibration, and safety role the design assumes, with preparation time budgeted.
- Confirm the design matches the stated enrollment, room, and staffing ratio, and treat a materially different class size as a redesign of participation, feedback, and assessment rather than a rescaling.
- Check preparation, facilitation, grading, feedback, training, maintenance, and versioning—not only class time.
- Verify room, laboratory, software, data, equipment, and support availability.
- Provide a realistic fallback and minimum viable implementation.
- Make workload tradeoffs visible and obtain instructor approval when resources constrain the preferred design.

## 12. Improvement evidence and research boundary

- Map each collected variable or observation to an improvement decision.
- Use more than satisfaction, participation, grades, or anecdote alone to claim learning.
- State alternative explanations and prohibit unsupported causal claims.
- Use disaggregated evidence only when lawful, ethical, privacy-preserving, sufficiently aggregated, and actionable.
- Distinguish ordinary course improvement, program evaluation, and research or dissemination.
- Pause research-like collection or dissemination for applicable institutional review, privacy, and data-governance guidance; de-identification alone is insufficient authorization.

## 13. Manual equivalents for deterministic checks

When code execution is unavailable, record the reviewer, date, file version, and result for each applicable check.

- **Course design brief:** enforce the documented heading hierarchy and selected completion profile; reject duplicate scalar fields used by a completion profile; locate TODO/TBD, bracketed placeholders, empty fields, and bare not-applicable values; verify status subsections, Current phase, and Next decision.
- **Alignment map:** select the table by required headers; reject malformed rows and duplicate headers; require one valid outcome ID for every populated row, including historical rows; verify outcome, cognitive demand, evidence, learning mechanism, activity/support, feedback/assessment, and controlled status. Reject a cognitive-demand value outside `remember`, `understand`, `apply`, `analyze`, `evaluate`, `create`.
- **Artifact manifest:** require artifact-family, variant, and required-variant columns even when blank for a standalone artifact; verify artifact type, identifiers, audiences, controlled statuses and validation tokens, every supplied review date as ISO, every active declared variant, variant/audience agreement, readiness evidence, production/accessibility/safety references, blockers, and local paths including Markdown links. Require a review reference or explicit not-required declaration on every teaching-ready row; reject pending, draft, review, blocked, unverified, and bare status values. Report unresolvable paths as structural errors; do not let retired variants satisfy active family requirements.
- **Assessment blueprint:** reject duplicate assessment-level scope or evidence declarations; verify declared assessed-outcome scope, controlled status/evidence level, valid outcome/item IDs, active coverage within that scope, positive finite time, nonnegative finite points, active dependency targets/cycles, barriers, and bounded formal-validation authorization. Count only outcomes with recognized active alignment status; exclude retired outcomes and items from current coverage; reject items outside scope. Reject a cognitive-demand value outside the controlled set. When an alignment map is available, compare the highest active item demand per outcome against that outcome's aligned demand and report an outcome whose entire active sample falls below it; do not report individual scaffolding items.
- **Course/curriculum map:** validate the required fields and syntax of historical rows, then exclude them from current decisions. Sort active rows by positive numeric Sequence rather than row order; validate stages, controlled status, tokenized external/internal prerequisites, cycles, finite positive workload, prior development, and the approved workload limit. Require every internal prerequisite to have earlier development or a declared external prior. Require introduction or a declared external prior and practice before mastery or assessment; enforce the complete ordered path at handoff. When practice distribution is being checked, report an outcome whose two or more active practice rows all fall in one module/week.
- **Project:** select the validator profile that matches the current phase (`establish`, `produce`, or `handoff`), then verify the declared engagement tier, matching brief tier, profile- and tier-required active state files, project-root path confinement, one canonical entry per resolved state file, one shared development-schema version, ISO dates synchronized between active state files and their index rows, bidirectional active-outcome coverage where required, cross-file outcome references, and applicable component validators.
- **Repository integrity:** open every relative Markdown link; compare the runtime package against the approved inventory; confirm every reference is routed from `SKILL.md`, every asset is mentioned by `SKILL.md` or a direct reference, and every validator is named in `SKILL.md`.

Use the same outcome vocabulary as the scripts: structural or parsing failures are errors; educational incompleteness, readiness gaps, or inconsistencies are findings. A manual pass does not authorize a stronger claim than the automated check would.
