# Course Coherence and Implementation

## Contents

1. Decide when course-level mapping is needed
2. Map development across the course
3. Check implementation load
4. Prepare teaching assistants and graders
5. Adjust the design to class size
6. Adjust the design to delivery mode
7. Make sustainability decisions
8. Plan implementation evidence
9. Separate improvement, evaluation, and research
10. Preserve a portable handoff

## 1. Decide when course-level mapping is needed

Use `assets/course-curriculum-map.md` for a full course, multi-week module, prerequisite sequence, or redesign that changes assessment timing. Skip it for a focused artifact when the surrounding course sequence is already confirmed and unaffected.

Ask which course, program, accreditation, or professional requirements apply. Map only requirements supplied or verified by the instructor; do not infer that an external framework governs the course.

The curriculum map covers development **within** one course or sequence. Mapping program outcomes across a degree, deciding which course owns which program outcome, and preparing program-level accreditation evidence are program-governance decisions that belong to the responsible program authority, not to this skill. When a program requirement is supplied, record it here as an authoritative constraint and show how this course contributes; do not construct or infer the program map itself, and do not present course-level evidence as program-level evidence.

### Produce course-level evidence for supplied accreditation indicators

Within that boundary, there is legitimate course-level work this skill can do when the program authority has already supplied the framework. When the instructor provides program-assigned outcomes or performance indicators — an accreditation outcome set, mapped indicators for this course, or a required course assessment report format — the skill may:

- map the supplied indicators onto the course's outcomes and assessments per `references/framework-crosswalk.md`, recording the framework, version, and assignment in the source register;
- tag rubric criteria and blueprint items with the indicators they evidence, so indicator-level data falls out of ordinary grading rather than requiring a parallel assessment;
- assemble a course-level evidence package — the mapping, the instruments, de-identified score distributions by indicator when an approved privacy path exists, and the instructor's observations — in the program's required format;
- flag supplied indicators that no current assessment samples, as gaps for the instructor to resolve.

The skill must not set or interpret attainment targets, judge whether an indicator is "met", decide which indicators this course should own, or generalize course evidence into program-level claims. Those judgments stay with the instructor and program authority; the skill prepares the evidence that makes them possible.

## 2. Map development across the course

For every important outcome, identify where students:

- activate prerequisites;
- encounter or **introduce** the outcome;
- **practice** with feedback;
- integrate or transfer learning;
- demonstrate **mastery** or are **assessed** consequentially.

Record a positive numeric sequence, display module or week, prerequisite outcomes, learning experience and evidence, feedback or assessment, expected workload, and controlled status. Use sequence—not row order or a text label—to establish chronology.

Inspect for:

- hidden, broken, circular, or late prerequisites that have no earlier development or declared external prior;
- outcomes assessed before adequate introduction and practice;
- practice massed in the module where the outcome is introduced and never revisited;
- long gaps without retrieval or use;
- confusable methods or models that are only ever practiced in separate blocks;
- redundant assessment or missing feedback;
- breadth without adequate depth;
- abrupt changes in representation, tool, or cognitive demand;
- clusters of deadlines or workload that create avoidable barriers;
- artifacts that are locally aligned but collectively incoherent.

The curriculum map is where distributed and interleaved practice are actually decided, because both are scheduling choices. An outcome introduced and practiced entirely within one module is massed no matter how many exercises that module contains. Place later practice inside subsequent work rather than in a review block, and set the gap from when the outcome is next needed. Warn the instructor that distributed and interleaved practice depress in-the-moment performance while improving retention, per `references/evidence-informed-design.md`.

Use the curriculum-map validator when available; `--check-practice-distribution` reports outcomes whose repeated practice sits in a single module. Apply the same checks manually when it cannot run.

Treat `retired` rows as historical state: do not let them satisfy current outcome development, prerequisite, evidence, or workload requirements. Require introduction or a declared external prior and practice to occur before mastery or consequential assessment. During Course-tier handoff, require every active aligned outcome to appear in the curriculum map and show that ordered progression. A working draft may expose these as gaps; it must not pass the handoff check until the progression is complete or the responsible owner retires or narrows the outcome explicitly.

## 3. Check implementation load

Use `assets/implementation-plan.md`. Estimate rather than hide:

- professor design and preparation time;
- TA or grader preparation, training, facilitation, and moderation;
- in-class time and transition cost;
- grading and feedback time;
- student preparation and task workload;
- room, laboratory, equipment, software, data, and accessibility support;
- technology setup, failure recovery, and help pathways;
- recurring maintenance, source updates, licensing, and versioning.

State whether an estimate is observed, calculated, instructor-supplied, or provisional. Do not label a design teachable based only on student-facing timing.

For a calculated student-workload estimate, use rate-based heuristics rather than intuition, and show the arithmetic so the instructor can correct the rates:

- **Reading** scales with purpose and difficulty: survey-level reading of accessible prose runs several times faster than close reading of dense technical text, which can drop below ten pages per hour when students must work examples as they read. Ask which kind the course expects, and rate the assigned text accordingly.
- **Problem sets** are best estimated from the instructor's own solve time multiplied by a novice factor — commonly three to five for material students are still learning — plus setup and write-up overhead, not from the number of problems.
- **Writing** estimates should count drafting, revision, and formatting, not just words; a page of polished technical writing routinely costs an hour or more of total time.
- **Videos and lectures** cost more than their run time once pausing and note-taking are included; discussion posts, quizzes, and administrative navigation each carry fixed overheads that dominate when tasks are small and frequent.

Sum per week, compare against the credit-hour expectation the institution defines, and treat a week that exceeds it as a finding for the instructor. Prior-offering student time reports — strong evidence per the student-reported-evidence guidance below — beat every heuristic; use them to calibrate the rates when they exist.

## 4. Prepare teaching assistants and graders

In most STEM courses, teaching assistants and graders deliver the design: they run laboratory sections, recitations, studios, and help hours, and they produce most of the feedback students actually receive. A design that assumes an expert facilitator and is delivered by an unprepared one becomes a different design. Treat their preparation as part of the artifact, not as a line in the workload estimate.

Ask what the teaching team actually is before assuming capability: number, appointment type, hours, disciplinary background, prior teaching experience, language of instruction, and whether they are graduate students, undergraduates, or staff. Do not assume that a graduate assistant has seen this course's content recently, or that an undergraduate assistant has seen it from the instructor's side.

Define and record:

- **Decision authority.** What an assistant may decide alone — a scoring judgment, a deadline exception, an accommodation request, a safety stop — and what must be escalated, to whom, and how quickly. Publish this to students as well as to the team.
- **Facilitation moves, not just answers.** Supply the questions to ask a stuck group, the common wrong turns and what each reveals, and what to do when a group finishes early or stalls. An answer key prepares a grader; it does not prepare a facilitator.
- **The disciplinary content of the session.** Give assistants the solution, the expected reasoning, and the known misconceptions in advance, and confirm they can work the task themselves before they facilitate it.
- **Calibration for scoring.** Apply `references/assessment-quality.md`. Independent scoring of shared examples before live grading, with disagreement diagnosed rather than averaged away.
- **Safety role.** For any hazard-bearing session, state explicitly what supervision an assistant provides, what they are qualified and authorized to supervise, what required training they hold, and the stop-work authority every assistant has. Route this through `references/stem-authenticity.md` and record it in `assets/safety-review.md`; do not treat assistant supervision as equivalent to the responsible owner's approval.
- **Feedback to the team.** A route for assistants to report what failed in the session, since they observe the design running and the instructor usually does not.

Budget the preparation time explicitly in `assets/implementation-plan.md`, including recurring per-session preparation and not only one orientation before the term. When preparation time is unavailable, say so and reduce the design's dependence on skilled facilitation rather than assuming it will be supplied.

## 5. Adjust the design to class size

Class size changes which designs are feasible, not merely how long they take. Ask for the size, the room, and the staffing ratio together, and re-check a design when any of them changes.

What changes as enrollment grows:

- **Feedback cannot stay individual and handwritten.** Shift toward common-error feedback to the whole class, exemplar comparison, structured peer feedback with an accountability check, rubric-coded comments, and automated checks for the parts that admit them — while keeping at least one channel of individual feedback on the outcomes that matter most.
- **Facilitation becomes indirect.** In a large room the instructor cannot reach most groups. Design for written directions that survive without oral repair, visible progress markers, and checkpoints the instructor can read from the front. Add assistants for coverage, and prepare them per §4.
- **Participation structures must not depend on volunteering.** Written commitment before discussion, structured pair and small-group protocols, and polling reach students that open questions never do.
- **Fixed seating and room shape are hard constraints**, not preferences. Verify what movement and grouping the room actually permits before designing for it.
- **Assessment logistics dominate.** Grading time, version security, make-up administration, and regrade volume scale with enrollment and often decide what is possible.
- **Individual detection weakens.** A struggling student is far less visible at 300 than at 30. Compensate with early low-stakes checks that surface difficulty as data rather than relying on noticing.

State the enrollment a design was built for. When adapting an existing design to a materially different size, treat it as a redesign of the participation, feedback, and assessment structure rather than a scaling of the same activity, and re-check the workload against §3.

## 6. Adjust the design to delivery mode

Delivery mode changes which designs are feasible in the same way class size does. Ask whether the course is in-person, synchronous online, asynchronous online, or hybrid — and for hybrid, which components are which — before designing participation, feedback, or assessment. A design built for a physical room does not port to an asynchronous course by recording the lectures; treat a mode change as a redesign of the interaction structure.

What changes when the course is partly or fully online:

- **Directions must survive without oral repair.** In an asynchronous course there is no circulating instructor. Written and recorded directions carry the entire facilitation load, so validate them as if no clarifying question can be asked — because for many students none will be.
- **Interaction must be designed, not assumed.** Co-presence produces incidental interaction; online courses produce none unless the design schedules it. Decide deliberately where instructor–student and student–student interaction occur, at what cadence, and with what expectations. Where regular and substantive interaction is an institutional or regulatory requirement for the modality, record it as an authoritative constraint from the institution rather than inferring its terms.
- **Discussion is an activity format, not a default.** An online discussion needs the same mechanism justification as any activity: a genuine reason students must engage each other's reasoning, a structured protocol, and visible criteria. A weekly "post and reply twice" requirement with no interdependence is participation theater, and students treat it accordingly.
- **Asynchronous pacing removes the session as the unit of design.** Replace in-session checkpoints with distributed low-stakes checks that surface difficulty as data, per the class-size guidance — the individual-detection problem of the large room is the default condition of the asynchronous course.
- **Laboratory and studio outcomes need an explicit modality decision.** Simulation, take-home kits, remote instrument access, and recorded demonstration differ in which outcomes they can evidence — a simulation can carry modeling and interpretation outcomes but not apparatus-handling ones. Map each laboratory outcome to what the online alternative can actually evidence, mark what is lost, and route safety for any take-home physical work per `references/stem-authenticity.md`.
- **Assessment conditions change.** Timed unproctored online assessment changes the construct and the fairness profile; apply the permitted-AI and fairness guidance in `references/assessment-quality.md` rather than importing an in-person exam unchanged. Check bandwidth, device, time-zone, and caregiving constraints as construct-irrelevant barriers.
- **Technology failure is a student-facing contingency.** Define what a student does when the platform, proctoring tool, or upload fails, and publish it in advance; ad-hoc exception handling is where online courses lose fairness.

State the delivery mode a design was built for in the design brief, and re-check accessibility: mode changes move the artifact set (captions, transcripts, document structure, platform navigation) that the accessibility review must cover.

## 7. Make sustainability decisions

When the strongest pedagogical option exceeds available resources, present:

```markdown
Decision: sustainable implementation

Preferred design:
Learning benefit:
Implementation load:
Unavailable resource or constraint:

Options:
1. Preserve the design and obtain support.
2. Use a lower-load adaptation while preserving the objective.
3. Pilot a smaller scope and collect implementation evidence.

Minimum viable implementation:
Tradeoff and risk:
Instructor choice:
```

Do not silently transfer workload to instructors, teaching assistants, graders, accessibility staff, or students. Record reuse and maintenance plans for repeated offerings.

## 8. Plan implementation evidence

Use `assets/implementation-evidence-plan.md` before collecting or analyzing learning evidence.

Define:

- the improvement question and decision it will inform;
- the outcome, behavior, experience, participation, or implementation measure;
- baseline or comparison evidence when available and appropriate;
- data source, timing, and minimum necessary variables;
- quantitative and qualitative evidence that complement each other;
- a decision rule for keep, revise, investigate, or stop;
- limitations and alternative explanations;
- privacy, retention, access, and deletion requirements.

Do not infer learning from satisfaction, participation, grades, or anecdotes alone. Do not claim causality from an uncontrolled before/after comparison.

### Use student-reported evidence for what it is good for

Students are the only available source on much of what determines whether a design works, and treating all student report as untrustworthy discards usable evidence.

Student report is **strong** evidence about:

- actual time on task and workload distribution across a week or term;
- which directions, notation, or interfaces were unclear;
- where they became stuck, and what they did next;
- access, participation, and belonging barriers they encountered;
- whether resources, help pathways, and technology were usable and available;
- what they believe they were supposed to be learning.

Student report is **weak** evidence about:

- whether learning occurred, and how much;
- the relative effectiveness of two instructional approaches;
- their own mastery, which correlates poorly with performance;
- the quality of a design they have no comparison for.

Design accordingly. Ask about experience, load, clarity, and barriers; use performance evidence for learning claims. A short mid-term feedback round — what helps learning, what impedes it, what the student can do differently — is a low-cost, high-value practice, especially when the instructor tells students what changed as a result. Report student-experience findings as student-reported experience, never restated as a learning outcome.

Collect only what maps to a decision, avoid unnecessary identifiers, and apply the improvement/evaluation/research boundary below before any dissemination.

Use disaggregated evidence only when it is lawful, ethical, sufficiently aggregated to protect privacy, educationally actionable, and approved under applicable governance. Small groups may make de-identification impossible.

## 9. Separate improvement, evaluation, and research

Classify the intended use before collecting new data:

- **ordinary course improvement:** informs teaching in the course and follows normal institutional practice;
- **program or institutional evaluation:** informs an authorized program decision and follows applicable governance;
- **research or dissemination:** may contribute generalizable knowledge, test a research claim, or be shared beyond ordinary educational operations.

De-identification does not by itself authorize research. When the purpose, dissemination plan, intervention, consent, or data use may cross into research, pause that part of the workflow and ask the instructor to consult the applicable institutional review, privacy, and data-governance authorities.

Continue ordinary material design and non-research reflection when they remain authorized and separable.

## 10. Preserve a portable handoff

Include the curriculum map, implementation plan, evidence plan, source notes, validation reports, unresolved decisions, and the next action in the portable bundle when they exist.

Before claiming cross-client support, verify that a second client can recover:

- confirmed, assumed, and open state;
- current phase and next decision;
- outcome and artifact identifiers;
- provenance and unresolved limitations;
- tool capabilities and fallbacks;
- privacy classifications without identifiable student data.

Do not claim a client passed because the Markdown files are syntactically readable. Run the same educational scenario and compare the decisions, required safeguards, and artifact relationships.
