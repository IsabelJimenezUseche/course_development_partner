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
10. Engineering authenticity when applicable
11. Implementation feasibility and sustainability
12. Improvement evidence and research boundary
13. Manual equivalents for deterministic checks

## 1. Severity and reporting

Classify each finding:

- **Blocker:** unsafe, invalid, unsolvable, materially unfair, inaccessible for required use, corrupt, or unusable.
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
- Match cognitive demand across outcome, activity, and assessment.
- Ensure every important outcome has learning support and evidence.
- Remove or justify orphan activities and assessments.
- Ensure engagement serves learning rather than replacing it.
- Check that rubric criteria and weights reflect objective importance.
- For course-level work, check prerequisite flow, outcome development, assessment timing, feedback opportunities, and workload across the sequence.

## 4. Scaffolding and readiness

- Activate or support prerequisites.
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

## 10. Engineering authenticity when applicable

- Require engineering formulation, analysis, design, experimentation, interpretation, or judgment rather than a themed calculation alone.
- Verify applicable standards, multiple constraints, uncertainty, risk, and tradeoffs.
- Include safety, welfare, ethical, lifecycle, environmental, social, or stakeholder consequences when they materially affect the decision.
- Allow multiple defensible alternatives when evidence and reasoning support them.
- Require qualified instructor review of consequential technical, safety, ethical, or standards claims.

## 11. Implementation feasibility and sustainability

- Estimate professor, TA, grader, student, technology-support, and accessibility-support workload.
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

- **Course design brief:** enforce the documented heading hierarchy and selected completion profile; locate TODO/TBD, bracketed placeholders, empty fields, and bare not-applicable values; verify status subsections, Current phase, and Next decision.
- **Alignment map:** select the table by required headers; reject malformed rows and duplicate headers; require one valid outcome ID per row; verify outcome, evidence, activity/support, feedback/assessment, and controlled status.
- **Artifact manifest:** verify artifact type, identifiers, audiences, controlled statuses and validation tokens, ISO dates, every declared variant, variant/audience agreement, readiness evidence, production/accessibility references, blockers, and local paths including Markdown links.
- **Assessment blueprint:** verify controlled status/evidence level, valid outcome/item IDs, required outcome coverage, finite positive time/points, dependency targets/cycles, barriers, and bounded formal-validation authorization.
- **Course/curriculum map:** sort by positive numeric Sequence rather than row order; validate stages, controlled status, tokenized external/internal prerequisites, cycles, finite positive workload, prior development, and the approved workload limit.
- **Project:** select the validator profile that matches the current phase (`establish`, `produce`, or `handoff`), then verify the project index, required active state files, one shared development-schema version, ISO dates, cross-file outcome references, and applicable component validators.
- **Repository integrity:** open every relative Markdown link; compare the runtime package against the approved inventory; confirm every reference is routed from `SKILL.md`, every asset is mentioned by `SKILL.md` or a direct reference, and every validator is named in `SKILL.md`.

Use the same outcome vocabulary as the scripts: structural or parsing failures are errors; educational incompleteness, readiness gaps, or inconsistencies are findings. A manual pass does not authorize a stronger claim than the automated check would.
