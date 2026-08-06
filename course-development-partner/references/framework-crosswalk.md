# Framework Crosswalk

Read this reference when the educator names or supplies an external framework: an accreditation outcome set, a learning taxonomy, a named pedagogy format, or a named grading scheme. It maps supplied frameworks onto this skill's internal structure so the educator can keep working in their own vocabulary.

The neutrality rule is unchanged: never assume that a framework governs a course because of the institution, discipline, or country. Map a framework only when the educator supplies it or confirms it applies, and record the supplied version, since frameworks revise their categories over time. The mappings below are working correspondences to reduce translation burden, not equivalence claims.

## Contents

1. Map accreditation outcome frameworks
2. Map learning taxonomies to the cognitive-demand tokens
3. Map design frameworks already embodied in this skill
4. Map named pedagogy formats to mechanisms
5. Map named grading schemes
6. Record the mapping

## 1. Map accreditation outcome frameworks

When the educator supplies an accreditation outcome set — ABET-style student outcomes, Washington Accord graduate attributes, CDIO syllabus sections, or a national or program equivalent — treat it as an authoritative constraint per `references/course-coherence-and-implementation.md` and map each supplied outcome into the alignment structure:

- Record the supplied outcome verbatim in the source register with its framework, version, and effective date; accreditation bodies renumber and reword outcomes across cycles.
- Derive one or more course-level observable outcomes from each supplied outcome that the course actually develops, and link them: the supplied outcome is the parent claim, the course outcome is what students demonstrably do here. A supplied outcome such as "an ability to apply engineering design to produce solutions that meet specified needs" spans several course outcomes with different cognitive demands; do not force it into one row.
- Technical supplied outcomes (analysis, experimentation, design) map naturally onto `apply`–`create` tokens. Professional supplied outcomes (teamwork, ethics, communication, lifelong learning) usually need the professional-skill guidance in `references/state-contract.md`, and team-based ones need the separate-claims structure in `references/assessment-quality.md`.
- Where the framework's design and experimentation outcomes apply, `references/stem-authenticity.md` supplies the matching task dimensions — constraints, standards, safety, welfare, stakeholders, uncertainty — so an authentic task usually evidences the supplied outcome without extra apparatus.

Deciding which course owns which program outcome, setting attainment targets, and judging program-level attainment remain program-governance decisions; see the boundary and the bounded course-level evidence pattern in `references/course-coherence-and-implementation.md`.

## 2. Map learning taxonomies to the cognitive-demand tokens

The six controlled tokens in `references/state-contract.md` — `remember`, `understand`, `apply`, `analyze`, `evaluate`, `create` — correspond closely to the revised Bloom cognitive-process dimension (Anderson–Krathwohl). An educator working in that taxonomy can map level to token directly, with one caution: the revised taxonomy also carries a knowledge dimension (factual, conceptual, procedural, metacognitive) that the tokens do not encode. When that dimension matters to the design, record it in the outcome text or the design log rather than inventing tokens.

For other taxonomies, map onto the nearest token and keep the original level in the outcome text or design log:

- **SOLO:** unistructural and multistructural responses usually sit at `remember`/`understand`; relational at `analyze`/`evaluate`; extended abstract at `evaluate`/`create`.
- **Webb Depth of Knowledge:** DOK 1 ≈ `remember`/`understand`; DOK 2 ≈ `apply`; DOK 3 ≈ `analyze`/`evaluate`; DOK 4 typically spans `evaluate`/`create` over extended work.
- **Program- or discipline-specific taxonomies:** ask the educator which token best matches each level's target performance rather than guessing from level names.

Do not add unmapped values to state files — they disable the demand checks. A supplied level that maps poorly onto any token is usually a sign the outcome is doing two jobs; propose splitting it.

## 3. Map design frameworks already embodied in this skill

Several widely used frameworks are already present in substance under neutral language. When the educator names one, point to where it lives rather than adding a parallel process:

- **Constructive alignment / backward design (Biggs; Wiggins–McTighe):** the core chain — outcome → evidence of learning → activity → support → feedback or assessment — in `SKILL.md` and `references/design-workflow.md`. Backward design's "acceptable evidence before activities" is step 3 before step 5 of the workflow.
- **Universal Design for Learning:** the multiple-means guidance for engagement, representation, and action or expression in `references/evidence-informed-design.md` §7, with the construct-preserving versus construct-changing distinction this skill adds. UDL adoption does not replace the individual-accommodation process; keep them distinct per `references/accessibility-and-compliance.md`.
- **Transparent assignment design (purpose–task–criteria):** the requirement that purpose and success criteria be visible to students, in `references/design-workflow.md` §5 and `references/evidence-informed-design.md` §8.
- **Scientific teaching / evidence-based instructional practice initiatives:** the mechanism-and-evidence discipline of `references/evidence-informed-design.md` and `references/evidence-source-protocol.md`.

When institutional initiatives require documenting use of a named framework, record the requirement as an authoritative constraint and produce the documentation in the framework's own vocabulary, mapped from the state files.

## 4. Map named pedagogy formats to mechanisms

Educators ask for formats by name. Honor the request, but design it as `references/evidence-informed-design.md` §2 requires: identify the mechanism the format depends on, and check the conditions without which the format keeps its name and loses its effect. The table gives the load-bearing mechanism and the most common fidelity failure for formats faculty request most often.

| Named format | Load-bearing mechanism | Most common fidelity failure |
|---|---|---|
| Peer instruction / concept questions | Individual commitment to a prediction, then argumentation with a peer holding a different answer, then resolution with feedback | Skipping the individual first vote, or questions that test recall so there is nothing to argue about |
| POGIL-style guided inquiry | Structured team processing of models before terminology, with rotating roles | Worksheets that tell before asking; roles assigned but never rotated or used |
| Just-in-time teaching | Pre-class conceptual work whose responses reshape the session | Pre-class quizzes graded for correctness but never read, so the session ignores what students revealed |
| Flipped classroom | Moving first exposure out of class to spend class time on supported practice and feedback | Recording lectures without redesigning class time; class becomes review, not practice |
| Studio / SCALE-UP formats | Sustained group work with circulating facilitation and public checkpoints | Room or staffing cannot support facilitation; see class-size guidance in `references/course-coherence-and-implementation.md` |
| Problem-based learning | An ill-structured problem encountered before the content it motivates, with facilitated self-directed learning | Problems with one right answer, or content lectured first so the problem is an exercise |
| Project-based learning | An extended authentic deliverable requiring integration across outcomes | Sole terminal deliverable with no milestone evidence; see `references/artifact-patterns.md` on multi-week projects |
| Model-eliciting activities | A client-driven task whose deliverable is a generalizable model, revealing student thinking | Grading only the final answer rather than the model and its documentation |
| Productive failure | Attempting a problem before instruction so the subsequent instruction lands on prepared ground | Treating the failure phase as graded performance, or omitting the consolidation instruction it exists to prepare |

Two rules govern every row. First, the format is not the outcome: confirm the mechanism serves the stated outcome before adopting the name. Second, the in-the-moment performance cost warnings for desirable difficulties apply to several of these formats — tell students why the work feels harder, per `references/evidence-informed-design.md` §5.

## 5. Map named grading schemes

The grading system belongs to the course owner; ask rather than infer, per `references/assessment-quality.md` §8. When the educator names a scheme, that section's alternative-grading guidance covers how instrument design changes under specifications, standards-based, and mastery schemes. Record the named scheme and its rules in the course-design brief so instrument-level scoring logic can be checked against it.

## 6. Record the mapping

Record every applied crosswalk in the design log and, for authoritative supplied frameworks, in the source register: the framework, version, supplied outcome or level, the internal outcome IDs or tokens it maps to, and any residue that did not map. The mapping is a working aid for this course; do not present it as an official interpretation of the framework, and do not reuse it for a different framework version without rechecking.
