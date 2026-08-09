# Worked Example

One module carried end to end, to show what the other references produce when they are applied together. Read it when the rules are clear but their combined output is not, or when an instructor asks what the process actually delivers.

The example is deliberately ordinary: an introductory measurement topic that recurs across chemistry, physics, biology, and engineering. Adapt the disciplinary surface; the structure transfers.

The mode is Co-design, so the example shows the conversation, not just its products. `> Checkpoint:` lines mark where a turn ended and the instructor answered; everything between two checkpoints happened in one turn. An engagement that produced these artifacts without these exchanges would be Rapid work mislabeled — the artifacts might be identical, but the mode failed.

## Contents

1. The request
2. Establish what students already know
3. Set the outcome and its evidence
4. Reject the first design
5. Place it in the course
6. Write the context brief
7. Storyboard the session
8. Blueprint the assessment
9. Draft the rubric
10. Validate
11. What was not produced
12. The Focused-tier contrast

## 1. The request

> "My students can compute a standard deviation but they treat every difference between two numbers as real. Second-year lab course, 60 students, one 110-minute session, two TAs. Can you build me something better than the current worksheet?"

Engagement tier: **Project** — one connected artifact family, consequential because it feeds a graded lab report. Mode: **Co-design**.

Confirmed: course level, class size, session length, staffing, the instructor's observation.
Assumed: students have met mean, standard deviation, and significant figures — flagged for correction.
Open: whether the module must serve a program measurement outcome.

## 2. Establish what students already know

Per `references/evidence-informed-design.md` §3, the current student model comes from evidence, not intuition.

The instructor supplies prior-offering lab reports. Across them, the recurring pattern is stable: students compare two means digit by digit, and report a difference as real whenever the digits differ. Uncertainty is computed, reported in a table, and then not used in the conclusion.

Recorded in `source-register.md` as:

```markdown
Claim: Students in this course treat any numerical difference between two means as a real difference and do not use uncertainty in their conclusions.
Fit: Observed in this course, prior two offerings, n≈40 reports.
Strength: Strong for this population; not generalized further.
```

This is *observed-in-course* evidence — the highest-fit category available. No published instrument was needed.

## 3. Set the outcome and its evidence

The instructor's first phrasing is "understand measurement uncertainty." That is not observable, and its demand is ambiguous. Reworded against the chain **outcome → evidence → activity → support → feedback**:

| Outcome ID | Observable learning outcome | Cognitive demand | Evidence of learning | Learning mechanism | Learning activity/support | Feedback or assessment | Status |
|---|---|---|---|---|---|---|---|
| LO-4 | Decide whether two measured quantities differ, and justify the decision using their uncertainties | evaluate | A written recommendation that states the comparison, the uncertainty basis, and the limits of the claim | conceptual change through discrepant evidence | Paired-sample comparison with contrasting cases | Structured peer feedback in session; scored in the lab report | approved |

The demand is `evaluate`, not `apply`: the target performance is a judgment under uncertainty, not the computation feeding it. Per `references/state-contract.md`, the demand is recorded for the target performance, and the assessment must reach it somewhere.

> Checkpoint: the reworded outcome went to the instructor with one sentence of reasoning — "understand" cannot be assessed, and the reports show the failure is the judgment, not the computation. The instructor approved the wording and the `evaluate` demand; the program measurement outcome stayed Open.

## 4. Reject the first design

The obvious activity — give students two datasets, have them compute means and uncertainties, ask which is larger — is rejected under `references/evidence-informed-design.md` §2: *reject an engaging activity when students can complete it without the intended reasoning.* Students can produce every number and still compare digits at the end. It exercises `apply` while the outcome names `evaluate`.

The design that survives makes the judgment unavoidable:

- Students receive **three** paired comparisons, not one. In the first, the intervals overlap heavily; in the second, they are clearly separated; in the third, they are marginal. Only the third requires a defended judgment, and the first two build the contrast that makes it legible.
- Students commit to a decision **before** computing, so the discrepancy between intuition and evidence is theirs to resolve rather than announced by the instructor.
- The deliverable is a recommendation to a named decision-maker, not a number.

This is the conceptual-change cycle of §4 — elicit, make evidence visible, examine the discrepancy, reconstruct, re-test, reflect — instantiated as a session.

> Checkpoint: both designs went to the instructor as a decision card — the compute-and-compare version (familiar, low preparation, but assessable without the target reasoning) against the commit-first three-comparison design (targets the judgment, needs three new datasets). The instructor chose the second and asked that the arithmetic supports be fully droppable in session; §7's contingency row exists because of that answer.

## 5. Place it in the course

Course-tier mapping, per `references/course-coherence-and-implementation.md`. The prerequisite outcome LO-2 is shown so the excerpt validates on its own. The point of interest is LO-4's second practice row: it is deliberately in a later module, on a different measurement, so the practice is distributed rather than massed.

| Sequence | Module/week | Outcome ID | Developmental stage | Outcome prerequisites | Learning experience/evidence | Feedback/assessment | Expected student workload (hours) | Status |
|---|---|---|---|---|---|---|---|---|
| 3 | 2 | LO-2 | introduce | none | Uncertainty of a single measurement | Worked-example feedback | 2 | approved |
| 5 | 3 | LO-2 | practice | none | Repeat-measurement exercise | In-session feedback | 2 | approved |
| 7 | 4 | LO-4 | introduce | LO-2 | Prediction, then paired-comparison session | In-session peer and TA feedback | 3 | approved |
| 8 | 4 | LO-4 | practice | LO-2 | Lab report on the session data | Scored rubric with revision | 3 | approved |
| 12 | 7 | LO-4 | practice | LO-2 | Comparison embedded in the thermal-properties lab | Instructor feedback | 2 | approved |
| 18 | 11 | LO-4 | assess | LO-2 | Novel comparison with a marginal result | Scored rubric | 2 | approved |

Running `validate_course_curriculum_map.py --check-practice-distribution` reports nothing, because the two practice rows sit in modules 4 and 7. Had both been in module 4, it would have flagged them.

The module-11 assessment is a *new* comparison with a marginal result, not the session data reused — otherwise it tests recall of a conclusion.

## 6. Write the context brief

Abridged from `assets/context-brief.md`:

```markdown
Setting: Materials receiving inspection at a small manufacturer.
Student role: Technician advising the purchasing decision.
Decision: Recommend whether to accept a second supplier's material as equivalent.
Concept or model: Mean, standard uncertainty, and the comparison of two uncertain quantities.
Data students receive: Two sets of measured specimens per comparison, with instrument specification.
Assumptions: Specimens are representative; the instrument is calibrated; no systematic offset between batches.
Uncertainty, risk, or sensitivity: Marginal case; the recommendation changes if the sample is smaller than assumed.
Safety/ethics: A false "equivalent" recommendation transfers risk to whoever uses the part.
Why this context improves the learning task: The decision has a cost either way, so "the numbers are different" is not an answer.
Instructor approval status: approved
```

The context is doing work: it supplies a decision-maker, a consequence, and a reason that a bare numerical comparison is insufficient. Per `references/stem-authenticity.md`, a calculation becomes authentic only when its result informs a credible decision.

> Checkpoint: the brief above was the entire preview for this turn — no storyboard yet, per the preview-smallest-structure rule. The instructor questioned whether second-year students know what a receiving inspection is, and the session now opens with two sentences establishing the role; the brief's approval line records the exchange.

## 7. Storyboard the session

Abridged from `assets/lesson-storyboard.md`, 110 minutes.

| Time | Purpose | Student action | Instructor/TA action | Evidence/checkpoint | Access/participation note |
|---|---|---|---|---|---|
| 0–10 | Opening / elicit | Individually predict, for all three pairs, whether the materials differ; commit in writing | Collect predictions; do not correct | Distribution of predictions | Written commitment, so participation does not require speaking |
| 10–40 | Active work | In pairs, compute means and uncertainties for pairs 1 and 2 | TAs circulate on computation only | Correct intervals for the two clear cases | Worked reference sheet available |
| 40–55 | Examine discrepancy | Compare own prediction to the interval picture; name what the prediction assumed | Surface two contrasting predictions anonymously | Students articulate the assumption | Anonymous surfacing avoids exposure |
| 55–85 | Reconstruct / decide | Take the marginal pair 3; write a recommendation with its basis and limits | Prompt: "what would change your recommendation?" | Draft recommendation | Template with sentence stems |
| 85–100 | Peer feedback | Exchange recommendations; check the basis and stated limits against criteria | Model one exchange | Annotated peer drafts | Criteria supplied in writing |
| 100–110 | Closure | Note what changed in their reasoning and what transfers | Name the transfer target in module 7 | Exit note | — |

Contingencies: if time runs short, drop pair 2 and keep the marginal case, which carries the outcome. If the computation stalls, distribute the precomputed intervals — the target is the judgment, not the arithmetic.

Note the load management from §6: the arithmetic is scaffolded and can be handed over entirely, because it is not the target construct. Removing it protects the outcome instead of weakening it.

## 8. Blueprint the assessment

Abridged from `assets/assessment-blueprint.md`:

- Assessed outcome scope: LO-4
- Evidence level claimed: classroom-reviewed

| Item ID | Outcome(s) | Intended interpretation/use | Evidence claim | Cognitive demand | Item type | Dependency | Expected time (min) | Points | Construct-irrelevant barriers | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| A-11 | LO-4 | Formative check | Computes a standard uncertainty correctly | apply | short answer | independent | 5 | 3 | none identified | approved |
| A-12 | LO-4 | Summative; contributes to lab-report grade | Decides and justifies using the uncertainty basis | evaluate | extended response | independent | 25 | 12 | Reading load of the scenario; scenario kept to 120 words | approved |

A-11 sits below the outcome's demand and is legitimate — it is a scaffolding check. A-12 reaches `evaluate`. Running `validate_assessment_blueprint.py --alignment-map alignment-map.md` passes. Had A-12 been omitted, leaving only A-11, it would report:

```text
GAP: LO-4: highest active item demand apply is below the aligned outcome demand evaluate
```

That is the check earning its place: every number in the blueprint would still be correct, the coverage count would still show LO-4 sampled, and the assessment would still be measuring the wrong thing.

## 9. Draft the rubric

Orientation: **balanced**, per `references/artifact-patterns.md` §9, because partial reasoning and more than one defensible recommendation exist. Criteria weighted toward the objective:

| Criterion | Weight | Achieved | Developing | Not yet |
|---|---|---|---|---|
| Uses uncertainty as the basis of the comparison | 40% | Comparison rests on the uncertainty ranges, correctly interpreted | Ranges computed and mentioned, but the conclusion rests on the means | Conclusion rests on the difference in digits |
| States the recommendation and its consequence | 25% | Clear recommendation addressed to the decision-maker, with the risk of being wrong | Recommendation given without consequence | No recommendation |
| States limits and what would change the decision | 25% | Names a specific condition that would reverse it | Generic hedging | No limits stated |
| Computation and reporting | 10% | Correct values, units, and reasonable figures | Minor errors that do not change the decision | Errors that invalidate the comparison |

Two rules recorded with it: a computational slip that does not change the decision is penalized once, under the last criterion only — not again through the conclusion criteria, per the double-penalty check. And *either* recommendation on the marginal pair can earn full credit if the basis and limits are sound, because the outcome is the justification, not the verdict.

The 10% weight on computation is the visible consequence of the alignment decision. It will surprise students, so the weighting is stated in advance.

> Checkpoint: the criteria, weights, orientation, and the two scoring rules were presented before any descriptor was written — the rubric preview the artifact pattern prescribes. The instructor accepted the 10% computation weight after seeing the tradeoff stated plainly ("this grades the judgment; the arithmetic is a gate, not the target") and asked that the weighting be announced in advance — which is why the previous sentence exists. Consequential scoring remains provisional until the course owner approves it for operational use.

## 10. Validate

Passes run per `references/validation-checklists.md`:

- **Disciplinary correctness** — instructor independently confirmed the three datasets produce the intended overlap, separation, and marginal cases. Blocker if the "marginal" pair is not actually marginal.
- **Data–task fit** — the mean-and-uncertainty computation was executed on each of the three delivered files, not on a description of them: `scripts/validate_dataset.py` against `--representation uncertainty` for each, then the comparison by hand. One file failed the first pass — its replicate column had been exported with a units row that made every value text — and was re-exported before the row was written. Each check is a row in `data-task-record.md`, linked from the manifest's `Data-task-fit evidence` column; the `data-task-fit` token was added only after that. A token with no record behind it would have said the same thing while proving nothing.
- **Alignment** — demand match confirmed by the blueprint validator against the alignment map.
- **Scaffolding** — arithmetic support present and explicitly droppable; the module-11 assessment removes the template.
- **Feasibility** — 110 minutes with two TAs for 60 students; contingency defined for the most likely overrun.
- **Accessibility** — written commitment instead of required speaking; anonymous surfacing; sentence stems; criteria supplied in writing rather than orally.
- **Assessment fairness** — alternative valid recommendations admitted; double penalty prevented.
- **Evidence** — the student-model claim is recorded with its population and marked as course-observed, not generalized.

Findings raised: one **Important** — the lab-report deadline falls in the same week as two other module deadlines; workload clustering flagged for the instructor's decision. One **Polish** — supplier names in the scenario shortened to reduce reading load.

## 11. What was not produced

- No slide deck. Nothing in the session needs projection that the handout does not carry better.
- No accessibility conformance claim. The design choices are recorded; no artifact was tested against a WCAG target, so no claim is made.
- No effectiveness claim. The module is aligned, feasible, and reviewed. Whether it improves learning is a question for the implementation-evidence plan, and the answer is not yet available.

That last omission is the pattern the rest of the package protects: the work is finished and honestly bounded, not finished and oversold.

## 12. The Focused-tier contrast

The machinery above is Project-tier machinery, justified because the artifact family feeds a graded report. Most requests are smaller, and the tier rules mean most requests never see any of it. For contrast, the same skill handling a Focused request:

> "I need a practice worksheet on series-parallel resistor combinations for Friday's recitation. 50 minutes, students have had the lecture."

No state files, no mode discussion, no tier announcement. The response asks at most the questions that change the design — here, two: what students should be able to do by the end (compute equivalent resistance, or *select* a reduction strategy and check the result?), and where they went wrong last year. Then it drafts the worksheet with a progression that ends above pure execution, produces the matching solution key with common errors, states inline the two checks performed (independent solution of every item; directions usable without oral repair) and the one thing not checked (timing is an estimate — no prior-offering data), and stops.

The Confirmed/Assumed/Open record lives in two sentences of the reply, not in a file. The design reasoning is the same — outcome before activity, demand named, key verified independently — but the overhead is proportionate to a one-session, low-stakes artifact. If the instructor then says "actually, make this a graded quiz with a rubric," the work becomes consequential and the Project-tier structure starts earning its cost. The tier follows the stakes; it is never the deliverable.
