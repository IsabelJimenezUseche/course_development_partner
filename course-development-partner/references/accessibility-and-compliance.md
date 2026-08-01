# Accessibility, Disability-Law, and Technical-Standards Awareness

Use this reference for digital content, documents, media, assessments, accommodations, disability law, WCAG, third-party learning technology, or institutional accessibility requirements. Support accessible design and bounded review; do not provide legal advice or make institutional compliance decisions.

## Contents

1. Establish authority and dates
2. Keep claims distinct
3. Separate required and recommended WCAG checks
4. Design access from the beginning
5. Apply artifact-specific checks
6. Test with complementary methods
7. Handle third parties and exceptions
8. Report bounded findings
9. Maintain authoritative sources

## 1. Establish authority and dates

Ask for the smallest facts needed to route the work:

- institution type and jurisdiction when relevant;
- delivery setting and intended applications;
- authoritative accessibility policy, accommodation process, procurement requirements, and decision owner;
- required technical standard with exact version, level, scope, and authority;
- source publication/revision date and last-verification date;
- policy effective/revision date;
- applicable legal or institutional compliance deadline;
- local release, remediation, review, or approval date.

Do not merge these dates. Prefer current authoritative requirements over summaries. If authority, applicability, or a conflict is unresolved, record it as Open and route the decision to the institution's authorized accessibility, disability, legal, procurement, or risk process. Do not request diagnoses or unnecessary disability information.

## 2. Keep claims distinct

Record separately:

- **Legal or regulatory authority:** an applicable requirement identified by an authoritative source.
- **Institutional policy:** current accessibility, procurement, accommodation, and exception rules.
- **Required technical target:** the exact named standard, version, level, and scope.
- **Recommended design target:** a stronger or more current target adopted for quality.
- **Review evidence:** methods, versions, tested scope, results, and untested scope.
- **Individual accommodation:** an authorized person-specific process that remains available even when universal design is used.

Do not use disability law, WCAG conformance, universal design, accommodations, and institutional policy as interchangeable terms. Never determine that an exception, fundamental alteration, undue burden, equivalent facilitation, or conforming alternate version applies; route those decisions to authorized personnel.

## 3. Separate required and recommended WCAG checks

Apply the exact criterion set named by the governing target. Record additional current-design checks separately.

- For a **WCAG 2.1** target, test the applicable WCAG 2.1 A/AA criteria, including Parsing 4.1.1 where required.
- For a **WCAG 2.2** target, test the WCAG 2.2 A/AA criteria. WCAG 2.2 adds criteria including Focus Not Obscured (Minimum) 2.4.11, Dragging Movements 2.5.7, Target Size (Minimum) 2.5.8, Consistent Help 3.2.6, Redundant Entry 3.3.7, and Accessible Authentication (Minimum) 3.3.8; it removes 4.1.1 from the WCAG 2.2 criterion set.
- When WCAG 2.1 governs but WCAG 2.2 is used as a recommended design target, report two results: governing-target findings and additional 2.2 findings.
- Do not silently translate a result between versions.

For non-web documents and software, use the current WCAG2ICT guidance to understand how a chosen WCAG version may apply. Treat WCAG2ICT as informative guidance rather than a source that independently creates requirements.

## 4. Design access from the beginning

- Identify the essential learning objective and construct.
- Remove barriers unrelated to the construct.
- Offer multiple ways to engage, obtain information, or respond when they preserve the construct.
- Keep approved accommodations available.
- Avoid requiring rapid speech, precise mouse control, color perception, hearing, or vision unless that ability is part of the approved construct.
- Provide comparable timing, information, privacy, independence, and opportunity rather than delayed access alone.
- Identify support workload, procurement lead time, remediation ownership, and a usable contingency before release.

If an option may change the construct, ask the responsible course owner and authorized accommodation process to decide before describing it as equivalent.

## 5. Apply artifact-specific checks

### Web, LMS, and interactive content

Check semantic structure, page title and language, landmarks, headings, labels, instructions, errors, status messages, keyboard operation, focus order and visibility, navigation, link purpose, zoom/reflow, contrast, non-color cues, time limits, motion, flashing, pointer alternatives, and authentication as required by the selected version. Include embedded and third-party components.

### Documents and PDFs

Use true headings and lists, descriptive links, meaningful alternatives, structured tables, logical reading/tab order, sufficient contrast, usable forms, accessible equations, document language, and metadata. Preserve an editable source. Inspect PDF tags and semantic order; visual correctness and tag presence are not sufficient.

### Presentations

Use unique slide titles, readable type, strong contrast, non-color cues, logical object order, text alternatives, accessible tables/charts, and captions or transcripts. Provide an accessible companion when the deck cannot carry all required information accessibly.

### Spreadsheets and data visualizations

Use descriptive sheet names, a clear starting location, structured regions, headers, formula/navigation notes, non-color cues, readable formats, chart descriptions, and a logical keyboard path. Avoid merged cells, blank-cell layout, or visual position as the only source of meaning.

### Audio and video

Provide accurate synchronized captions, transcript, speaker identification, relevant sound information, accessible controls, and audio description or an equivalent when essential visual information is otherwise unavailable. Human-review generated text for names, terminology, equations, and timing.

### Assessments and learning activities

Check directions, navigation, timing, response mode, media, proctoring, simulations, equations, diagrams, group roles, and permitted assistive technology. Ensure access options do not reveal answers, add construct-irrelevant load, or change the target without approval.

## 6. Test with complementary methods

No single method establishes accessibility or legal compliance. Use a proportionate combination of:

1. source structure and metadata inspection;
2. automated checking with tool, version, ruleset, and coverage recorded;
3. keyboard and visible-focus review;
4. zoom, reflow, contrast, color-independence, and responsive-layout review;
5. screen-reader or other assistive-technology review when warranted;
6. human review of captions, alternatives, equations, and reading order;
7. rendered or playback inspection in intended applications;
8. disabled-user or accessibility-specialist testing when stakes, novelty, or policy warrants it.

Record untested criteria, technologies, states, pages, and user paths. Treat an automated pass only as evidence for the rules and content inspected.

## 7. Handle third parties and exceptions

Inventory publisher platforms, simulations, proctoring systems, videos, library resources, linked files, widgets, and student-facing tools. Record ownership, required use, procurement status, accessibility documentation, known barriers, support route, and contingency.

Do not assume vendor ownership removes institutional responsibility or that archived, third-party, password-protected, individualized, old, or difficult content is automatically excepted. Obtain authoritative review for exceptions and release with unresolved required-use barriers.

When a barrier remains, document the affected task, educational/access effect, interim access plan proposed by authorized personnel, owner, response time, remediation date, and approvals still required.

## 8. Report bounded findings

Use `assets/accessibility-review.md`. Treat a required-use barrier that prevents equal participation, effective communication, independent use, or demonstration of the intended construct as a Blocker unless authorized guidance determines otherwise.

Use bounded language:

- `Reviewed against the listed checks` for partial coverage.
- `Automated check passed for the recorded ruleset` for automated coverage only.
- `Conforms to [standard/version/level] for the tested scope` only when complete evidence and the authorized process support that exact claim.
- Make a legal-compliance or exception claim only when an authorized institutional process supplies it; the assistant must not make it.

Record unresolved barriers, untested scope, accommodation dependencies, third-party risks, responsible owners, dates, and required approvals in the accessibility review, artifact manifest, and implementation plan.

## 9. Maintain authoritative sources

Verify current requirements at the time of use. Useful starting points include:

- U.S. Department of Justice Title II web/mobile rule: <https://www.ada.gov/resources/2024-03-08-web-rule/>
- U.S. Department of Education technology accessibility: <https://www.ed.gov/laws-and-policy/civil-rights-laws/disability-discrimination/disability-discrimination-key-issues/disability-discrimination-technology-accessibility>
- W3C WCAG 2.1: <https://www.w3.org/TR/WCAG21/>
- W3C WCAG 2.2: <https://www.w3.org/TR/WCAG22/>
- W3C WCAG2ICT: <https://www.w3.org/TR/wcag2ict-22/>

Record the exact governing text or institutional interpretation used, version, scope, dates, and source authority. If sources conflict or applicability is uncertain, pause the claim and seek authorized guidance.
