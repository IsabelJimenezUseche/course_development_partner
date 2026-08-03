# STEM Authenticity

Read this reference when the teaching task involves engineering, engineering technology, computing, or a laboratory or quantitative science. Do not impose it on unrelated disciplines.

Authenticity means that students do the discipline's characteristic work — formulating, modeling, measuring, designing, interpreting, and judging under real constraints — rather than executing a procedure whose result changes nothing. The dimensions below are shared across STEM; the disciplinary profiles adapt them.

## Establish authority

Ask which institutional, program, professional, accreditation, code, or standard requirements apply. Treat instructor-provided and institutional requirements as authoritative. Treat external frameworks as conditional benchmarks until the instructor confirms applicability.

Do not assume that a particular accreditation framework, professional code, disciplinary society guideline, or national standard governs the course.

## Build an authentic task

Require students to formulate, model, analyze, design, experiment, interpret, or exercise disciplinary judgment. A calculation becomes authentic only when its result informs a credible decision or claim.

Consider each dimension and include it when it materially affects the objective or decision:

- affected stakeholders, users, or populations;
- specified needs, questions, or success criteria;
- technical and nontechnical constraints;
- applicable standards, codes, protocols, or regulations;
- public health, safety, and welfare;
- professional, ethical, and research-integrity responsibilities;
- global, cultural, social, environmental, and economic effects;
- uncertainty, variability, error, risk, sensitivity, and resilience;
- lifecycle, maintenance, sustainability, and unintended consequences;
- experimental or observational evidence, model limits, and data quality;
- communication with technical and nontechnical audiences;
- tradeoffs among multiple defensible alternatives.

Do not force every dimension into every task. Record why a dimension is irrelevant. Do not omit a consequential safety, ethical, stakeholder, or uncertainty issue merely to make production easier.

## Use a decision brief

```markdown
Disciplinary practice targeted:
Problem owner and affected stakeholders:
Decision, design, or claim responsibility:
Specified need or question:
Evidence or data available:
Models, tools, instruments, or experiments:
Applicable standards or requirements:
Constraints and tradeoffs:
Uncertainty, error, and risk:
Safety, welfare, and ethical considerations:
Lifecycle or societal effects:
Expected disciplinary judgment:
What makes the task authentic:
Dimensions considered but omitted, with rationale:
```

## Apply the disciplinary profile

Use the profile that matches the work. A course may need more than one.

### Engineering and engineering technology

Emphasize design under competing constraints, applicable codes and standards, safety and public welfare, uncertainty and margin, lifecycle and sustainability effects, and sociotechnical tradeoffs. Require a defensible recommendation, not only a correct number.

### Computing and data disciplines

Emphasize problem specification, correctness and testing, complexity and scale, data provenance and quality, reproducibility, security and privacy, accessibility of what is built, and the human consequences of deployed systems. Treat a working implementation as necessary but not sufficient evidence of the reasoning behind it. Where students use generated code or automated tooling, make the review, verification, and justification the assessed work.

### Laboratory and experimental sciences

Emphasize question formulation, experimental design and controls, measurement and instrument limits, uncertainty propagation, data handling and recordkeeping, replication, and the boundary between what the data support and what the student concluded. A confirmatory exercise with a known answer teaches procedure; say so plainly rather than describing it as inquiry.

### Mathematics and quantitative reasoning

Emphasize model selection and its assumptions, representation and translation between forms, argument and proof structure, interpretation of results in context, and the limits of the model. Require students to state assumptions and to say what would make the model inappropriate.

## Preserve appropriate complexity

Represent ill-structured and sociotechnical problems without implying that one calculation determines the only acceptable answer. Distinguish:

- facts and authoritative requirements;
- model-based estimates;
- assumptions and value judgments;
- stakeholder priorities;
- uncertain or missing evidence;
- technically feasible alternatives;
- the instructor-approved basis for evaluating judgment.

Allow multiple defensible recommendations when students use valid evidence and reasoning. A solution key should identify required constraints, unacceptable safety or ethical violations, defensible alternatives, and the limits of the model answer.

## Treat laboratory and field safety as a release blocker

This applies whenever students will handle equipment, chemicals, biological material, energized systems, radiation, machinery, vehicles, drones, field sites, or any physical hazard.

The skill may help draft, organize, or format safety material. It may not originate the safety basis, and its output is never the authority.

- Require review and approval by the qualified responsible person — the instructor of record, laboratory manager, safety officer, or the institution's environmental-health-and-safety function — before any safety content reaches students. Record the owner, governing document, verification dates, and approval in `safety-review.md` from `assets/safety-review.md`, and reference it from the artifact manifest.
- Treat hazard identification, risk assessment, exposure limits, personal protective equipment specifications, chemical incompatibilities, waste disposal, energy control and lockout, containment level, emergency and spill response, and equipment operating limits as **generated drafts requiring verification against the authoritative institutional document, manufacturer documentation, or safety data sheet**. Cite the specific source and its date in the source register.
- Do not infer a hazard classification, a control measure, or a disposal route from a substance name, a procedure description, or a similar published protocol.
- Do not present a safety section as complete when a required institutional document was unavailable. Mark it blocked and identify what is missing.
- An unverified, missing, or unreviewed safety element is a **Blocker** under `references/validation-checklists.md`. It prevents teaching-ready status regardless of the quality of the rest of the artifact.
- This rule holds in every interaction mode. Auto mode may prepare the draft and the verification list; it may not clear the blocker.

Apply the same standard to field work, human-subject or animal protocols, and data-handling requirements, routing each to the authority that governs it.

## Validate authenticity

- Does the context change the formulation, method, evidence, interpretation, or decision?
- Must students use disciplinary judgment in addition to correct calculation or execution?
- Are relevant standards, protocols, and constraints represented accurately?
- Are uncertainty, error, risk, and limitations proportionate to the course level?
- Are public consequences and stakeholder perspectives treated credibly?
- Can students justify more than one defensible solution when appropriate?
- Does the rubric reward the objective rather than conformity to one unstated design preference?
- Has a qualified instructor reviewed consequential technical, safety, ethical, or standards claims?
- Has the responsible safety owner approved every hazard-bearing element?
